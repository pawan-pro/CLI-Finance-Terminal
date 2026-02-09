import { User, ChatMessage } from '../types';

const USERS_KEY = 'nexus_users';
const CURRENT_USER_KEY = 'nexus_current_user';
const CHAT_CHANNEL = 'nexus_public_chat';

// --- Auth Persistence ---

export const getUsers = (): User[] => {
  const stored = localStorage.getItem(USERS_KEY);
  return stored ? JSON.parse(stored) : [];
};

export const saveUser = (user: User) => {
  const users = getUsers();
  users.push(user);
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
};

export const getCurrentUser = (): User | null => {
  const stored = localStorage.getItem(CURRENT_USER_KEY);
  return stored ? JSON.parse(stored) : null;
};

export const setCurrentUser = (user: User | null) => {
  if (user) {
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
  } else {
    localStorage.removeItem(CURRENT_USER_KEY);
  }
};

// --- Real-time Chat Simulation ---

// BroadcastChannel allows communication between tabs/windows on same origin
const chatChannel = new BroadcastChannel(CHAT_CHANNEL);

export const sendPublicMessage = (message: ChatMessage) => {
  // Store in local buffer for history (optional, usually would be DB)
  const history = getChatHistory();
  history.push(message);
  if (history.length > 50) history.shift(); // Keep last 50
  localStorage.setItem('nexus_chat_history', JSON.stringify(history));

  // Broadcast to other tabs
  chatChannel.postMessage(message);
};

export const getChatHistory = (): ChatMessage[] => {
  const stored = localStorage.getItem('nexus_chat_history');
  return stored ? JSON.parse(stored) : [];
};

export const subscribeToChat = (callback: (msg: ChatMessage) => void) => {
  chatChannel.onmessage = (event) => {
    callback(event.data);
  };
  return () => {
    chatChannel.onmessage = null;
  };
};