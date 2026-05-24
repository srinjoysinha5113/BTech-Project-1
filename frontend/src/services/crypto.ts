/**
 * Crypto service using the native Web Crypto API for AES-GCM.
 */
class CryptoService {
  /**
   * Import a raw byte array as an AES-GCM key.
   */
  static async importKey(rawKey: Uint8Array): Promise<CryptoKey> {
    return window.crypto.subtle.importKey(
      'raw',
      rawKey,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt', 'decrypt']
    );
  }

  /**
   * Encrypt plaintext using AES-256-GCM.
   */
  static async encrypt(plaintext: string, key: CryptoKey) {
    const encoder = new TextEncoder();
    const data = encoder.encode(plaintext);
    const nonce = window.crypto.getRandomValues(new Uint8Array(12)); // 96-bit nonce for GCM

    const encrypted = await window.crypto.subtle.encrypt(
      { name: 'AES-GCM', iv: nonce },
      key,
      data
    );

    const encryptedArray = new Uint8Array(encrypted);
    
    // The Web Crypto API includes the auth tag at the end of the ciphertext
    // GCM default tag length is 128 bits (16 bytes)
    const ciphertext = encryptedArray.slice(0, -16);
    const authTag = encryptedArray.slice(-16);

    return {
      ciphertext: this.arrayBufferToBase64(ciphertext),
      nonce: this.arrayBufferToBase64(nonce),
      authTag: this.arrayBufferToBase64(authTag),
    };
  }

  /**
   * Decrypt ciphertext using AES-256-GCM.
   */
  static async decrypt(
    ciphertextBase64: string,
    key: CryptoKey,
    nonceBase64: string,
    authTagBase64: string
  ): Promise<string> {
    const ciphertext = this.base64ToArrayBuffer(ciphertextBase64);
    const nonce = this.base64ToArrayBuffer(nonceBase64);
    const authTag = this.base64ToArrayBuffer(authTagBase64);

    // Reconstruct the data (ciphertext + tag) for Web Crypto API
    const data = new Uint8Array(ciphertext.byteLength + authTag.byteLength);
    data.set(new Uint8Array(ciphertext), 0);
    data.set(new Uint8Array(authTag), ciphertext.byteLength);

    const decrypted = await window.crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: nonce },
      key,
      data
    );

    const decoder = new TextEncoder().encoding === 'utf-8' ? new TextDecoder() : new TextDecoder('utf-8');
    return decoder.decode(decrypted);
  }

  // Helper utilities
  static arrayBufferToBase64(buffer: ArrayBuffer | Uint8Array): string {
    const binary = String.fromCharCode(...new Uint8Array(buffer));
    return window.btoa(binary);
  }

  static base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = window.atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }
}

export default CryptoService;
