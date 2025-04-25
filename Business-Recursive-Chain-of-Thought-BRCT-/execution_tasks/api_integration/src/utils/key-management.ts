/**
 * Secure API key management utilities
 */

import * as crypto from 'crypto';
import * as fs from 'fs';
import * as path from 'path';

/**
 * Encrypted API key structure
 */
interface EncryptedKey {
  provider: string;
  encryptedKey: string;
  iv: string;
}

/**
 * API key in storage
 */
interface StoredKey {
  provider: string;
  encryptedKey: string;
  iv: string;
  createdAt: string;
  expiresAt?: string;
}

/**
 * API key storage manager
 */
export class KeyManager {
  /**
   * Master encryption key
   */
  private encryptionKey: Buffer;
  
  /**
   * Path to key storage file
   */
  private storagePath: string;
  
  /**
   * In-memory key cache
   */
  private keyCache: Map<string, string> = new Map();

  /**
   * Create a new key manager instance
   * 
   * @param encryptionKey Master key for encrypting API keys (hex string or Buffer)
   * @param storagePath Path to key storage file
   */
  constructor(encryptionKey: string | Buffer, storagePath: string) {
    // Ensure encryption key is properly formatted
    if (typeof encryptionKey === 'string') {
      // If hex string, convert to buffer
      this.encryptionKey = Buffer.from(encryptionKey, 'hex');
    } else {
      this.encryptionKey = encryptionKey;
    }
    
    // Ensure key is proper length for AES-256
    if (this.encryptionKey.length !== 32) {
      throw new Error('Encryption key must be 32 bytes (256 bits) for AES-256');
    }
    
    this.storagePath = storagePath;
    
    // Ensure storage directory exists
    const storageDir = path.dirname(storagePath);
    if (!fs.existsSync(storageDir)) {
      fs.mkdirSync(storageDir, { recursive: true });
    }
    
    // Create storage file if it doesn't exist
    if (!fs.existsSync(storagePath)) {
      fs.writeFileSync(storagePath, JSON.stringify([], null, 2));
    }
  }

  /**
   * Store an API key for a provider
   * 
   * @param provider Provider name
   * @param apiKey API key to store
   * @param expiresInDays Optional expiration in days
   * @returns True if successful
   */
  storeKey(provider: string, apiKey: string, expiresInDays?: number): boolean {
    try {
      // Encrypt the API key
      const encrypted = this.encryptKey(apiKey);
      
      // Calculate expiration if provided
      let expiresAt: string | undefined = undefined;
      if (expiresInDays) {
        const expDate = new Date();
        expDate.setDate(expDate.getDate() + expiresInDays);
        expiresAt = expDate.toISOString();
      }
      
      // Create storage record
      const keyData: StoredKey = {
        provider: provider.toLowerCase(),
        encryptedKey: encrypted.encryptedKey,
        iv: encrypted.iv,
        createdAt: new Date().toISOString(),
        expiresAt
      };
      
      // Read existing keys
      const keys = this.readKeyStorage();
      
      // Remove any existing key for this provider
      const filteredKeys = keys.filter(k => k.provider !== provider.toLowerCase());
      
      // Add new key
      filteredKeys.push(keyData);
      
      // Write back to storage
      fs.writeFileSync(this.storagePath, JSON.stringify(filteredKeys, null, 2));
      
      // Add to cache
      this.keyCache.set(provider.toLowerCase(), apiKey);
      
      return true;
    } catch (error) {
      console.error('Error storing API key:', error);
      return false;
    }
  }

  /**
   * Get an API key for a provider
   * 
   * @param provider Provider name
   * @returns API key if found, null otherwise
   */
  getKey(provider: string): string | null {
    const providerKey = provider.toLowerCase();
    
    // Check cache first
    if (this.keyCache.has(providerKey)) {
      return this.keyCache.get(providerKey) || null;
    }
    
    try {
      // Read from storage
      const keys = this.readKeyStorage();
      const keyData = keys.find(k => k.provider === providerKey);
      
      if (!keyData) {
        return null;
      }
      
      // Check if expired
      if (keyData.expiresAt) {
        const expiryDate = new Date(keyData.expiresAt);
        if (expiryDate < new Date()) {
          // Key is expired
          console.log(`API key for ${provider} has expired`);
          return null;
        }
      }
      
      // Decrypt key
      const apiKey = this.decryptKey({
        provider: keyData.provider,
        encryptedKey: keyData.encryptedKey,
        iv: keyData.iv
      });
      
      // Add to cache
      this.keyCache.set(providerKey, apiKey);
      
      return apiKey;
    } catch (error) {
      console.error('Error retrieving API key:', error);
      return null;
    }
  }

  /**
   * Remove a stored API key
   * 
   * @param provider Provider name
   * @returns True if successful
   */
  removeKey(provider: string): boolean {
    try {
      const providerKey = provider.toLowerCase();
      
      // Read existing keys
      const keys = this.readKeyStorage();
      
      // Remove key for this provider
      const filteredKeys = keys.filter(k => k.provider !== providerKey);
      
      // Write back to storage
      fs.writeFileSync(this.storagePath, JSON.stringify(filteredKeys, null, 2));
      
      // Remove from cache
      this.keyCache.delete(providerKey);
      
      return true;
    } catch (error) {
      console.error('Error removing API key:', error);
      return false;
    }
  }

  /**
   * List all providers with stored keys
   * 
   * @returns Array of provider names
   */
  listProviders(): string[] {
    try {
      const keys = this.readKeyStorage();
      return keys.map(k => k.provider);
    } catch (error) {
      console.error('Error listing providers:', error);
      return [];
    }
  }

  /**
   * Check if a key exists and is valid for a provider
   * 
   * @param provider Provider name
   * @returns True if a valid key exists
   */
  hasValidKey(provider: string): boolean {
    return this.getKey(provider) !== null;
  }

  /**
   * Rotate an API key (replace with a new one)
   * 
   * @param provider Provider name
   * @param newApiKey New API key
   * @param expiresInDays Optional expiration in days
   * @returns True if successful
   */
  rotateKey(provider: string, newApiKey: string, expiresInDays?: number): boolean {
    return this.storeKey(provider, newApiKey, expiresInDays);
  }

  /**
   * Read key storage file
   * 
   * @returns Array of stored keys
   */
  private readKeyStorage(): StoredKey[] {
    try {
      const data = fs.readFileSync(this.storagePath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      console.error('Error reading key storage:', error);
      return [];
    }
  }

  /**
   * Encrypt an API key
   * 
   * @param apiKey API key to encrypt
   * @returns Encrypted key data
   */
  private encryptKey(apiKey: string): EncryptedKey {
    // Generate a random initialization vector
    const iv = crypto.randomBytes(16);
    
    // Create cipher with AES-256-CBC
    const cipher = crypto.createCipheriv('aes-256-cbc', this.encryptionKey, iv);
    
    // Encrypt the API key
    let encrypted = cipher.update(apiKey, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    return {
      provider: '', // Filled in by caller
      encryptedKey: encrypted,
      iv: iv.toString('hex')
    };
  }

  /**
   * Decrypt an API key
   * 
   * @param encryptedData Encrypted key data
   * @returns Decrypted API key
   */
  private decryptKey(encryptedData: EncryptedKey): string {
    // Convert IV from hex to Buffer
    const iv = Buffer.from(encryptedData.iv, 'hex');
    
    // Create decipher
    const decipher = crypto.createDecipheriv('aes-256-cbc', this.encryptionKey, iv);
    
    // Decrypt the API key
    let decrypted = decipher.update(encryptedData.encryptedKey, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  /**
   * Generate a new random encryption key (for initial setup)
   * 
   * @returns Hex string of the generated key
   */
  static generateEncryptionKey(): string {
    // Generate a random 256-bit (32-byte) key
    return crypto.randomBytes(32).toString('hex');
  }
}
