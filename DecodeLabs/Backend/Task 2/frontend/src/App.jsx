import { useState, useEffect } from 'react';
import UserForm from './components/UserForm';
import UserList from './components/UserList';
import './App.css';

const API_URL = 'http://localhost:5000/api/users';

function App() {
  const [users, setUsers] = useState([]);
  const [editingUser, setEditingUser] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch users
  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_URL);
      if (!response.ok) throw new Error('Failed to fetch users');
      const data = await response.json();
      setUsers(data);
      setError(null);
    } catch (err) {
      setError('Failed to load users. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Create or Update User
  const handleSubmit = async (userData) => {
    try {
      const url = editingUser ? `${API_URL}/${editingUser.id}` : API_URL;
      const method = editingUser ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Something went wrong');
      }

      await fetchUsers();
      setEditingUser(null);
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  };

  // Delete User
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;
    
    try {
      const response = await fetch(`${API_URL}/${id}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error('Failed to delete user');
      
      await fetchUsers();
    } catch (err) {
      setError(err.message);
    }
  };

  // Set user for editing
  const handleEdit = (user) => {
    setEditingUser(user);
    setError(null);
  };

  const handleCancelEdit = () => {
    setEditingUser(null);
    setError(null);
  };

  return (
    <div className="app-container">
      <div className="background-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
      </div>
      
      <header className="app-header fade-in-down">
        <h1>Admin<span>Dashboard</span></h1>
        <p>Manage your users efficiently with a modern interface.</p>
      </header>

      <main className="app-content">
        <div className="left-panel">
          <UserForm 
            onSubmit={handleSubmit} 
            initialData={editingUser} 
            onCancel={handleCancelEdit}
            error={error}
          />
        </div>
        <div className="right-panel">
          {loading ? (
            <div className="loader glass-panel">Loading users...</div>
          ) : (
            <UserList 
              users={users} 
              onEdit={handleEdit} 
              onDelete={handleDelete} 
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
