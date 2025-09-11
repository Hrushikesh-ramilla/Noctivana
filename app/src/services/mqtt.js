import React, { createContext, useContext, useEffect, useState } from "react";
import MQTT from "react-native-mqtt";

const MqttContext = createContext(null);
const BROKER = "mqtt://edgewatch.local:8883";

export function MqttProvider({ children }) {
  const [client, setClient]   = useState(null);
  const [connected, setConn]  = useState(false);
  const [alerts, setAlerts]   = useState([]);

  useEffect(() => {
    const mqtt = MQTT.createClient({ uri: BROKER, clientId: "edgewatch-app" });
    mqtt.on("closed",   () => setConn(false));
    mqtt.on("error",    (e) => console.warn("MQTT error:", e));
    mqtt.on("connect",  () => {
      setConn(true);
      mqtt.subscribe("edgewatch/alert/#", 1);
    });
    mqtt.on("message", (topic, data) => {
      try {
        const payload = JSON.parse(data);
        setAlerts(prev => [payload, ...prev].slice(0, 100));
      } catch(e) {}
    });
    mqtt.connect();
    setClient(mqtt);
    return () => mqtt.disconnect();
  }, []);

  return (
    <MqttContext.Provider value={{ client, connected, alerts }}>
      {children}
    </MqttContext.Provider>
  );
}

export const useMqtt = () => useContext(MqttContext);
