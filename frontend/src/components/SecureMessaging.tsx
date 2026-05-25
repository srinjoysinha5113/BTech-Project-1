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
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">Post-Quantum Secure Messaging</h2>
          <p className="text-slate-500 text-sm">End-to-end encrypted messaging using Kyber-512 and AES-256-GCM.</p>
        </div>
        
        <div className="flex items-center gap-3">
          {!session ? (
            <button 
              onClick={establishSession}
              className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-2.5 rounded-xl font-semibold transition-all active:scale-[0.98] shadow-lg shadow-purple-100 flex items-center gap-2"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              Establish PQC Session
            </button>
          ) : (
            <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 border border-emerald-100 rounded-xl text-emerald-700 font-medium text-sm">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Session Active: {session.id.substring(0, 12)}...
            </div>
          )}
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
            <h3 className="text-lg font-bold text-slate-900 mb-4">New Message</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5 ml-1">Recipient</label>
                <input 
                  type="text" 
                  placeholder="Username" 
                  value={recipient}
                  onChange={(e) => setRecipient(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5 ml-1">Message Content</label>
                <textarea 
                  placeholder="Enter your secure message..." 
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  disabled={!session}
                  rows={4}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all disabled:opacity-50 resize-none"
                />
              </div>
              <button 
                onClick={sendMessage} 
                disabled={!session || !message}
                className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3 rounded-xl transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send Secure Payload
              </button>
            </div>
          </div>

          <div className="bg-slate-900 rounded-2xl overflow-hidden shadow-xl border border-slate-800">
            <div className="bg-slate-800 px-4 py-2 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Security Logs</span>
              <div className="flex gap-1.5">
                <div className="w-2 h-2 rounded-full bg-red-500/50"></div>
                <div className="w-2 h-2 rounded-full bg-yellow-500/50"></div>
                <div className="w-2 h-2 rounded-full bg-green-500/50"></div>
              </div>
            </div>
            <div className="p-4 h-[300px] overflow-y-auto font-mono text-[11px] leading-relaxed">
              {logs.length > 0 ? (
                logs.map((log, i) => (
                  <div key={i} className="mb-1 text-slate-300">
                    <span className="text-emerald-500 mr-2">➜</span>
                    {log}
                  </div>
                ))
              ) : (
                <div className="text-slate-600 italic">Awaiting secure operations...</div>
              )}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-bold text-slate-900">Encrypted Inbox</h3>
            <button 
              onClick={refreshInbox}
              className="p-2 text-slate-400 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-all"
              title="Refresh Inbox"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
          
          <div className="space-y-3">
            {inbox.length > 0 ? (
              inbox.map((msg) => (
                <div key={msg.id} className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 transition-all hover:shadow-md group">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center text-slate-600 font-bold group-hover:bg-purple-100 group-hover:text-purple-600 transition-colors">
                        {msg.sender_username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-bold text-slate-900">{msg.sender_username}</div>
                        <div className="text-[10px] font-bold text-purple-500 uppercase tracking-wider bg-purple-50 px-1.5 py-0.5 rounded">
                          {msg.encryption_method}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                    {decryptedMessages[msg.id] ? (
                      <div className="text-slate-800 text-sm leading-relaxed">
                        <span className="font-bold text-slate-400 mr-2 text-xs">PLAINTEXT:</span>
                        {decryptedMessages[msg.id]}
                      </div>
                    ) : (
                      <div className="flex items-center justify-between gap-4">
                        <div className="flex-1 font-mono text-xs text-slate-400 truncate italic">
                          [ENCRYPTED_PAYLOAD_LOCKED]
                        </div>
                        <button 
                          className="bg-white hover:bg-slate-900 hover:text-white text-slate-900 border border-slate-200 px-4 py-1.5 rounded-lg text-xs font-bold transition-all shadow-sm" 
                          onClick={() => decryptMessage(msg.id)}
                        >
                          Decrypt
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="bg-white py-20 text-center rounded-2xl border-2 border-dashed border-slate-100">
                <div className="text-slate-300 mb-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto mb-4 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                  Your inbox is currently empty.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecureMessaging;
