import Users from './components/Users';

const App: React.FC = () => {
  return (
    <div style={{ padding: '2rem' }}>
      <h1>Admin Users (temps réel)</h1>
      <Users />
    </div>
  );
};

export default App;
