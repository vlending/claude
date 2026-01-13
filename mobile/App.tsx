import React from 'react';
import { StyleSheet, Text, View, Button } from 'react-native';
import { StatusBar } from 'expo-status-bar';

export default function App() {
  const [apiStatus, setApiStatus] = React.useState<string>('Checking...');

  const checkAPI = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      setApiStatus(`✅ Connected: ${data.app} v${data.version}`);
    } catch (error) {
      setApiStatus(`❌ Failed to connect to API: ${error}`);
    }
  };

  React.useEffect(() => {
    checkAPI();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>먹은대로 🍽️</Text>
      <Text style={styles.subtitle}>Health Meal Coach</Text>

      <View style={styles.statusCard}>
        <Text style={styles.statusLabel}>Backend API Status:</Text>
        <Text style={styles.statusText}>{apiStatus}</Text>
      </View>

      <Button title="Refresh API Status" onPress={checkAPI} />

      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#666',
    marginBottom: 40,
  },
  statusCard: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statusLabel: {
    fontSize: 14,
    color: '#999',
    marginBottom: 8,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
  },
});
