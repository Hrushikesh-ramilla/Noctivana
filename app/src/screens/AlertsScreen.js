import React from "react";
import { View, Text, FlatList, StyleSheet } from "react-native";
import { useMqtt } from "../services/mqtt";

const SEVERITY_COLOR = { CRITICAL: "#ef4444", WARN: "#f59e0b", INFO: "#6b7280" };

function AlertCard({ item }) {
  const color = SEVERITY_COLOR[item.severity] || "#6b7280";
  return (
    <View style={[styles.card, {borderLeftColor: color}]}>
      <Text style={styles.severity}>{item.severity}</Text>
      <Text style={styles.type}>{item.type?.replace(/_/g," ").toUpperCase()}</Text>
      <Text style={styles.message}>{item.message}</Text>
      <Text style={styles.time}>{new Date(item.ts*1000).toLocaleTimeString()}</Text>
    </View>
  );
}

export default function AlertsScreen() {
  const { alerts, connected } = useMqtt();
  return (
    <View style={styles.container}>
      <View style={[styles.banner, {backgroundColor: connected?"#064e3b":"#450a0a"}]}>
        <Text style={styles.bannerText}>{connected ? "● Connected" : "○ Disconnected"}</Text>
      </View>
      <FlatList
        data={alerts}
        keyExtractor={(_, i) => i.toString()}
        renderItem={AlertCard}
        ListEmptyComponent={<Text style={styles.empty}>No alerts yet</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container:  { flex:1, backgroundColor:"#0d1117" },
  banner:     { padding:8, alignItems:"center" },
  bannerText: { color:"#fff", fontSize:12 },
  card:       { margin:8, padding:12, backgroundColor:"#161b22", borderRadius:8, borderLeftWidth:4 },
  severity:   { fontSize:11, color:"#6b7280", fontWeight:"bold" },
  type:       { fontSize:16, color:"#f9fafb", fontWeight:"bold", marginTop:2 },
  message:    { fontSize:13, color:"#d1d5db", marginTop:4 },
  time:       { fontSize:11, color:"#4b5563", marginTop:4 },
  empty:      { textAlign:"center", color:"#4b5563", marginTop:40, fontSize:14 },
});
