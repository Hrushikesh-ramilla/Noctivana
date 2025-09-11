import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import AlertsScreen  from "./src/screens/AlertsScreen";
import SessionScreen from "./src/screens/SessionScreen";
import SettingsScreen from "./src/screens/SettingsScreen";
import SetupScreen   from "./src/screens/SetupScreen";
import { MqttProvider } from "./src/services/mqtt";

const Tab = createBottomTabNavigator();

export default function App() {
  return (
    <MqttProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={{
            tabBarStyle: { backgroundColor: "#0d1117" },
            tabBarActiveTintColor: "#7c3aed",
            tabBarInactiveTintColor: "#6b7280",
            headerStyle: { backgroundColor: "#0d1117" },
            headerTintColor: "#f9fafb",
          }}>
          <Tab.Screen name="Alerts"   component={AlertsScreen}   options={{tabBarLabel:"Alerts"}} />
          <Tab.Screen name="Sessions" component={SessionScreen}   options={{tabBarLabel:"Sessions"}} />
          <Tab.Screen name="Settings" component={SettingsScreen}  options={{tabBarLabel:"Settings"}} />
          <Tab.Screen name="Setup"    component={SetupScreen}     options={{tabBarLabel:"Setup"}} />
        </Tab.Navigator>
      </NavigationContainer>
    </MqttProvider>
  );
}
