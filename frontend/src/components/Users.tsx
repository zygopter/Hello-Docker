// src/components/Users.tsx
import React, { useEffect, useState, useRef } from 'react';
import type { UserOut, UserIn } from '../types';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS   = import.meta.env.VITE_WS_URL  || 'ws://localhost:8000/ws/users';

const Users: React.FC = () => {
  const [users, setUsers] = useState<UserOut[]>([]);
  const [form, setForm] = useState<Partial<UserIn>>({});
  const [editId, setEditId] = useState<number | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Charge la liste initiale
  const fetchUsers = async () => {
    const res = await fetch(`${API}/users/`);
    setUsers(await res.json());
  };

  // Handlers CRUD
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const url    = editId ? `${API}/users/${editId}` : `${API}/users/`;
    const method = editId ? 'PUT' : 'POST';
    await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    setForm({});
    setEditId(null);
    // pas besoin de re-fetch : on attend l'événement WebSocket
  };

  const handleDelete = async (id: number) => {
    await fetch(`${API}/users/${id}`, { method: 'DELETE' });
    // idem, on attend l'événement
  };

  const startEdit = (u: UserOut) => {
    setForm({
      firstname: u.firstname,
      lastname:  u.lastname,
      nickname:  u.nickname,
      email:     u.email,
    });
    setEditId(u.id);
  };

  // Connexion WebSocket et gestion des messages
  useEffect(() => {
    fetchUsers();

    const ws = new WebSocket(WS);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WS connected');
    };

    ws.onmessage = (ev) => {
      const msg: {
        action: 'create' | 'update' | 'delete';
        user?: UserOut;
        user_id?: number;
      } = JSON.parse(ev.data);

      setUsers((prev) => {
        switch (msg.action) {
          case 'create':
            return msg.user! /* on sait qu'il existe */ 
              ? [...prev, msg.user]
              : prev;
          case 'update':
            return prev.map(u => u.id === msg.user!.id ? msg.user! : u);
          case 'delete':
            return prev.filter(u => u.id !== msg.user_id);
          default:
            return prev;
        }
      });
    };

    ws.onclose = () => {
      console.log('WS disconnected');
    };

    return () => {
      ws.close();
    };
  }, []);

  return (
    <div>
      <h2>Gestion des Users (WebSocket)</h2>

      <form onSubmit={handleSubmit} style={{ marginBottom: '1em' }}>
        <input
          placeholder="Prénom"
          value={form.firstname || ''}
          onChange={e => setForm({ ...form, firstname: e.target.value })}
          required
        />
        <input
          placeholder="Nom"
          value={form.lastname || ''}
          onChange={e => setForm({ ...form, lastname: e.target.value })}
          required
        />
        <input
          placeholder="Surnom"
          value={form.nickname || ''}
          onChange={e => setForm({ ...form, nickname: e.target.value })}
        />
        <input
          type="email"
          placeholder="Email"
          value={form.email || ''}
          onChange={e => setForm({ ...form, email: e.target.value })}
          required
        />
        <button type="submit">{editId ? 'Modifier' : 'Ajouter'}</button>
        {editId && (
          <button type="button" onClick={() => { setForm({}); setEditId(null); }}>
            Annuler
          </button>
        )}
      </form>

      <table border={1} cellPadding={5} style={{ width: '100%', textAlign: 'left' }}>
        <thead>
          <tr>
            <th>ID</th><th>Prénom</th><th>Nom</th><th>Surnom</th><th>Email</th><th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map(u => (
            <tr key={u.id}>
              <td>{u.id}</td>
              <td>{u.firstname}</td>
              <td>{u.lastname}</td>
              <td>{u.nickname}</td>
              <td>{u.email}</td>
              <td>
                <button onClick={() => startEdit(u)}>✏️</button>
                <button onClick={() => handleDelete(u.id)}>🗑️</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default Users;
