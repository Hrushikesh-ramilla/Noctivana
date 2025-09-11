import React, { useState } from "react";
import { View, Text, TouchableOpacity, ActivityIndicator, StyleSheet } from "react-native";

export default function SetupScreen() {
  const [step,    setStep]    = useState(0);
  const [loading, setLoading] = useState(false);
  const [status,  setStatus]  = useState("");

  const startScan = async () => {
    setLoading(true);
    setStatus("Scanning for EdgeWatch device...");
    // TODO: BLE scan via react-native-ble-plx
    setTimeout(() => {
      setStatus("Found EdgeWatch. Tap to pair.");
      setLoading(false);
      setStep(1);
    }, 3000);
  };

  const pair = async () => {
    setLoading(true);
    setStatus("Pairing with EdgeWatch...");
    setTimeout(() => {
      setStatus("Paired! Connection established.");
      setLoading(false);
      setStep(2);
    }, 2000);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Setup EdgeWatch</Text>
      {step === 0 && <TouchableOpacity style={styles.btn} onPress={startScan}><Text style={styles.btnText}>Scan for Device</Text></TouchableOpacity>}
      {step === 1 && <TouchableOpacity style={styles.btn} onPress={pair}><Text style={styles.btnText}>Connect & Pair</Text></TouchableOpacity>}
      {loading && <ActivityIndicator color="#7c3aed" style={{marginTop:20}} />}
      <Text style={styles.status}>{status}</Text>
      {step === 2 && <Text style={styles.ok}>✓ EdgeWatch is connected and monitoring</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex:1, backgroundColor:"#0d1117", padding:24, alignItems:"center", justifyContent:"center" },
  header:    { color:"#f9fafb", fontSize:24, fontWeight:"bold", marginBottom:32 },
  btn:       { backgroundColor:"#7c3aed", paddingHorizontal:32, paddingVertical:14, borderRadius:12 },
  btnText:   { color:"#fff", fontWeight:"bold", fontSize:16 },
  status:    { color:"#9ca3af", marginTop:20, textAlign:"center" },
  ok:        { color:"#34d399", marginTop:16, fontSize:16 },
});
