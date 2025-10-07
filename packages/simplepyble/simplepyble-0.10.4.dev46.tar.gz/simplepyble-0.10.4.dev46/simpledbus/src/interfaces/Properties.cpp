#include <simpledbus/advanced/Proxy.h>
#include <simpledbus/interfaces/Properties.h>

using namespace SimpleDBus;
using namespace SimpleDBus::Interfaces;

const AutoRegisterInterface<Properties> Properties::registry {
    "org.freedesktop.DBus.Properties",
    // clang-format off
    [](std::shared_ptr<Connection> conn, std::shared_ptr<Proxy> proxy) -> std::shared_ptr<SimpleDBus::Interface> {
        return std::make_shared<Properties>(conn, proxy);
    }
    // clang-format on
};

Properties::Properties(std::shared_ptr<Connection> conn, std::shared_ptr<Proxy> proxy)
    : Interface(conn, proxy, "org.freedesktop.DBus.Properties") {}

Holder Properties::Get(const std::string& interface_name, const std::string& property_name) {
    Message query_msg = Message::create_method_call(_bus_name, _path, "org.freedesktop.DBus.Properties", "Get");

    Holder h_interface = Holder::create_string(interface_name);
    query_msg.append_argument(h_interface, "s");

    Holder h_name = Holder::create_string(property_name);
    query_msg.append_argument(h_name, "s");

    Message reply_msg = _conn->send_with_reply_and_block(query_msg);
    Holder result = reply_msg.extract();
    return result;
}

Holder Properties::GetAll(const std::string& interface_name) {
    Message query_msg = Message::create_method_call(_bus_name, _path, "org.freedesktop.DBus.Properties", "GetAll");

    Holder h_interface = Holder::create_string(interface_name);
    query_msg.append_argument(h_interface, "s");

    Message reply_msg = _conn->send_with_reply_and_block(query_msg);
    Holder result = reply_msg.extract();
    return result;
}

void Properties::Set(const std::string& interface_name, const std::string& property_name, const Holder& value) {
    Message query_msg = Message::create_method_call(_bus_name, _path, "org.freedesktop.DBus.Properties", "Set");

    Holder h_interface = Holder::create_string(interface_name);
    query_msg.append_argument(h_interface, "s");

    Holder h_name = Holder::create_string(property_name);
    query_msg.append_argument(h_name, "s");

    query_msg.append_argument(value, "v");

    _conn->send_with_reply_and_block(query_msg);
}

void Properties::PropertiesChanged(const std::string& interface_name,
                                   const std::map<std::string, Holder>& changed_properties) {
    std::vector<std::string> invalidated_properties;
    PropertiesChanged(interface_name, changed_properties, invalidated_properties);
}

void Properties::PropertiesChanged(const std::string& interface_name,
                                   const std::vector<std::string>& invalidated_properties) {
    std::map<std::string, Holder> changed_properties;
    PropertiesChanged(interface_name, changed_properties, invalidated_properties);
}

void Properties::PropertiesChanged(const std::string& interface_name,
                                   const std::map<std::string, Holder>& changed_properties,
                                   const std::vector<std::string>& invalidated_properties) {
    Message signal_msg = Message::create_signal(_path, "org.freedesktop.DBus.Properties", "PropertiesChanged");

    Holder interface_h = Holder::create_string(interface_name);
    signal_msg.append_argument(interface_h, "s");

    Holder changed_properties_h = Holder::create_dict();
    for (const auto& [key, value] : changed_properties) {
        changed_properties_h.dict_append(Holder::STRING, key, value);
    }
    signal_msg.append_argument(changed_properties_h, "a{sv}");

    Holder invalidated_properties_h = Holder::create_array();
    for (const auto& property : invalidated_properties) {
        invalidated_properties_h.array_append(Holder::create_string(property));
    }
    signal_msg.append_argument(invalidated_properties_h, "as");
    _conn->send(signal_msg);
}

void Properties::message_handle(Message& msg) {
    if (msg.is_method_call(_interface_name, "GetAll")) {
        Holder interface_h = msg.extract();
        std::string iface_name = interface_h.get_string();

        std::shared_ptr<Interface> interface = proxy()->interface_get(iface_name);
        SimpleDBus::Holder properties = SimpleDBus::Holder::create_dict();
        {
            std::scoped_lock lock(interface->_property_update_mutex);
            for (const auto& [key, value] : interface->_properties) {
                properties.dict_append(SimpleDBus::Holder::Type::STRING, key, value);
            }
        }

        SimpleDBus::Message reply = SimpleDBus::Message::create_method_return(msg);
        reply.append_argument(properties, "a{sv}");
        _conn->send(reply);

    } else if (msg.is_method_call(_interface_name, "Get")) {
        Holder interface_h = msg.extract();
        std::string iface_name = interface_h.get_string();
        msg.extract_next();

        Holder property_h = msg.extract();
        std::string property_name = property_h.get_string();

        std::shared_ptr<Interface> interface = proxy()->interface_get(iface_name);

        bool property_exists = false;
        Holder property_value;
        {
            std::scoped_lock lock(interface->_property_update_mutex);
            property_exists = interface->_properties.find(property_name) != interface->_properties.end();
            if (property_exists) {
                property_value = interface->_properties[property_name];
            }
        }

        if (!property_exists) {
            SimpleDBus::Message reply = SimpleDBus::Message::create_error(msg, "org.freedesktop.DBus.Error.InvalidArgs", "Property not found");
            _conn->send(reply);
            return;
        }

        SimpleDBus::Message reply = SimpleDBus::Message::create_method_return(msg);
        reply.append_argument(property_value, "v");
        _conn->send(reply);

    } else if (msg.is_method_call(_interface_name, "Set")) {
        Holder interface_h = msg.extract();
        std::string iface_name = interface_h.get_string();
        msg.extract_next();

        Holder property_h = msg.extract();
        std::string property_name = property_h.get_string();
        msg.extract_next();

        Holder value_h = msg.extract();

        std::shared_ptr<Interface> interface = proxy()->interface_get(iface_name);
        {
            std::scoped_lock lock(interface->_property_update_mutex);
            // Only update the property if it exists.
            // TODO: Should we send an error message if the property doesn't exist?
            if (interface->_properties.find(property_name) != interface->_properties.end()) {
                interface->_properties[property_name] = value_h;
            }
        }

        SimpleDBus::Message reply = SimpleDBus::Message::create_method_return(msg);
        _conn->send(reply);

    } else if (msg.is_signal(_interface_name, "PropertiesChanged")) {
        Holder interface_h = msg.extract();
        std::string iface_name = interface_h.get_string();
        msg.extract_next();
        Holder changed_properties = msg.extract();
        msg.extract_next();
        Holder invalidated_properties = msg.extract();

        // If the interface is not loaded, then ignore the message.
        if (!proxy()->interface_exists(iface_name)) {
            return;
        }

        proxy()->interface_get(iface_name)->signal_property_changed(changed_properties, invalidated_properties);
    }
}