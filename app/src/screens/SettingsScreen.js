import React, { useState, useEffect } from "react";
import { View, Text, Switch, Slider, StyleSheet, ScrollView } from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useMqtt } from "../services/mqtt";

export default function SettingsScreen() {
  const { client } = useMqtt();
  const [privacyMode, setPrivacy] = useState(false);
  const [tempHigh,    setTempHigh] = useState(28);
  const [dbThresh,    setDbThresh] = useState(70);

  // Restore saved settings
  useEffect(() => {
    AsyncStorage.multiGet(["privacy","tempHigh","dbThresh"]).then(pairs => {
      const map = Object.fromEntries(pairs.filter(([_,v]) => v));
      if (map.privacy) setPrivacy(map.privacy === "true");
      if (map.tempHigh) setTempHigh(Number(map.tempHigh));
      if (map.dbThresh) setDbThresh(Number(map.dbThresh));
    });
  }, []);

  const publish = (key, value) => {
    AsyncStorage.setItem(key, String(value));
    const payload = JSON.stringify({ [key]: value });
    client?.publish("edgewatch/config", payload, 1, false);
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Settings</Text>

      <View style={styles.row}>
        <Text style={styles.label}>Privacy Mode (disable camera+mic)</Text>
        <Switch value={privacyMode} onValueChange={v => {setPrivacy(v); publish("privacy", v);}} />
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Temperature Alert Threshold: {tempHigh}°C</Text>
        <Slider minimumValue={20} maximumValue={35} step={0.5} value={tempHigh}
          onSlidingComplete={v => {setTempHigh(v); publish("tempHigh", v);}}
          minimumTrackTintColor="#7c3aed" />
      </View>

      <View style={styles.section}>
        <Text style={styles.label}>Sound Alert Threshold: {dbThresh} dB</Text>
        <Slider minimumValue={50} maximumValue={90} step={1} value={dbThresh}
          onSlidingComplete={v => {setDbThresh(v); publish("dbThresh", v);}}
          minimumTrackTintColor="#7c3aed" />
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex:1, backgroundColor:"#0d1117", padding:16 },
  header:    { color:"#f9fafb", fontSize:22, fontWeight:"bold", marginBottom:20 },
  row:       { flexDirection:"row", justifyContent:"space-between", alignItems:"center", marginVertical:12 },
  section:   { marginVertical:12 },
  label:     { color:"#d1d5db", fontSize:14, marginBottom:8 },
});
