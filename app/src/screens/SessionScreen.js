import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useMqtt } from "../services/mqtt";

export default function SessionScreen() {
  const { alerts } = useMqtt();
  const criticals = alerts.filter(a => a.severity === "CRITICAL").length;
  const warns     = alerts.filter(a => a.severity === "WARN").length;

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.header}>Current Session</Text>
      <View style={styles.card}>
        <Text style={styles.stat}>Critical Alerts: <Text style={styles.red}>{criticals}</Text></Text>
        <Text style={styles.stat}>Warnings: <Text style={styles.yellow}>{warns}</Text></Text>
        <Text style={styles.stat}>Total Events: {alerts.length}</Text>
      </View>
      <Text style={styles.note}>Full session history stored on device. Export via Settings.</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex:1, backgroundColor:"#0d1117", padding:16 },
  header:    { color:"#f9fafb", fontSize:22, fontWeight:"bold", marginBottom:20 },
  card:      { backgroundColor:"#161b22", borderRadius:8, padding:16, marginBottom:16 },
  stat:      { color:"#d1d5db", fontSize:16, marginVertical:4 },
  red:       { color:"#ef4444", fontWeight:"bold" },
  yellow:    { color:"#f59e0b", fontWeight:"bold" },
  note:      { color:"#4b5563", fontSize:12, textAlign:"center" },
});
