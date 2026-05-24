import React, { useState, useEffect } from "react";
import ApiService from "../services/api";
import CryptoService from "../services/crypto";

const SecureMessaging: React.FC = () => {
  const [session, setSession] = useState<{ id: string; key: CryptoKey } | null>(null);
  const [message, setMessage] = useState("");
  const [recipient, setRecipient] = useState("");
  const [logs, setLogs] = useState<string[]>([]);
  const [inbox, setInbox] = useState<any[]>([]);
  const [decryptedMessages, setDecryptedMessages] = useState<Record<number, string>>({});

  const addLog = (msg: string) => {
    setLogs(prev => {
        const timestamp = new Date().toLocaleTimeString();
        return ["(" + timestamp + ") " + msg, ...prev];
    });
  };

  const establishSession = async () => {
    try {
      addLog("Generating ephemeral Kyber parameters...");
      const mockPublicKey = "MOCK_KYBER_PUBLIC_KEY_BASE64";
      const response = await ApiService.createSession(mockPublicKey);
      addLog("PQC Session established with Backend.");
      addLog("Session ID: " + response.session_id.substring(0, 10));
      const demoKey = new Uint8Array(32).fill(1); 
      const cryptoKey = await CryptoService.importKey(demoKey);
      setSession({ id: response.session_id, key: cryptoKey });
    } catch (err: any) {
      addLog("Error: " + err.message);
    }
  };

  const sendMessage = async () => {
    if (!session || !message) return;
    try {
      addLog("Encrypting message with AES-256-GCM...");
      const encrypted = await CryptoService.encrypt(message, session.key);
      addLog("Sending PQC-secured payload...");
      await ApiService.sendMessageWithSession({
        session_id: session.id,
        recipient_username: recipient || undefined,
        aes_ciphertext: encrypted.ciphertext,
        aes_nonce: encrypted.nonce,
        aes_auth_tag: encrypted.authTag,
      });
      addLog("Message sent successfully!");
      setMessage("");
      refreshInbox();
    } catch (err: any) {
      addLog("Error: " + err.message);
    }
  };

  const decryptMessage = async (messageId: number) => {
    if (!session) {
        addLog("Establish a PQC session first to decrypt messages.");
        return;
    }
    try {
        addLog("Requesting backend decryption via active PQC session...");
        const response = await ApiService.decryptMessageWithSession(messageId, session.id);
        setDecryptedMessages(prev => ({ ...prev, [messageId]: response.plaintext }));
        addLog("Message decrypted successfully.");
    } catch (err: any) {
        addLog("Decryption failed: " + err.message);
    }
  };

  const refreshInbox = async () => {
    try {
      const messages = await ApiService.getInbox();
      setInbox(messages);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    refreshInbox();
  }, []);

  return (
    <div className="secure-messaging">
      <h2>Post-Quantum Secure Messaging</h2>
      
      <div className="session-controls">
        {!session ? (
          <button onClick={establishSession}>Establish PQC Session</button>
        ) : (
          <div className="session-info">
            <span className="status-badge">Session Active: {session.id.substring(0, 12)}...</span>
          </div>
        )}
      </div>

      <div className="message-form">
        <input 
          type="text" 
          placeholder="Recipient Username" 
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
        />
        <textarea 
          placeholder="Enter your secure message..." 
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={!session}
        />
        <button onClick={sendMessage} disabled={!session || !message}>
          Send Securely
        </button>
      </div>

      <div className="messaging-layout">
        <div className="logs-panel">
          <h3>Security Logs</h3>
          <div className="log-list">
            {logs.map((log, i) => (
              <div key={i} className="log-entry">{log}</div>
            ))}
          </div>
        </div>

        <div className="inbox-panel">
          <h3>Inbox</h3>
          <div className="message-list">
            {inbox.map((msg) => (
              <div key={msg.id} className="message-item">
                <div className="msg-header">From: {msg.sender_username}</div>
                <div className="msg-method">{msg.encryption_method}</div>
                <div className="msg-payload">
                    {decryptedMessages[msg.id] ? (
                        <div className="plaintext">Message: {decryptedMessages[msg.id]}</div>
                    ) : (
                        <button className="decrypt-btn" onClick={() => decryptMessage(msg.id)}>
                            Decrypt & Read
                        </button>
                    )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecureMessaging;
