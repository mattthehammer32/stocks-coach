import { useEffect } from 'react';
import { SafeAreaView, Text } from 'react-native';
import { registerForPush } from './src/push';

export default function App() {
  useEffect(() => {
    registerForPush(process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000', 'demo-user');
  }, []);
  return (
    <SafeAreaView style={{flex:1, alignItems:'center', justifyContent:'center'}}>
      <Text>Stocks Coach Mobile (push enabled)</Text>
    </SafeAreaView>
  );
}
