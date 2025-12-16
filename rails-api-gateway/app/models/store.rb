class Store < ApplicationRecord
  validates :shop_domain, presence: true, uniqueness: true
  
  # Encrypt access token before saving
  before_save :encrypt_token, if: :access_token_changed?
  
  attr_accessor :access_token
  
  def decrypted_access_token
    return nil unless encrypted_access_token
    
    cipher = OpenSSL::Cipher.new('AES-256-CBC')
    cipher.decrypt
    cipher.key = encryption_key
    
    decrypted = cipher.update(Base64.decode64(encrypted_access_token)) + cipher.final
    decrypted
  rescue
    nil
  end
  
  def access_token=(token)
    @access_token = token
    @access_token_changed = true
  end
  
  private
  
  def access_token_changed?
    @access_token_changed || false
  end
  
  def encrypt_token
    return unless @access_token
    
    cipher = OpenSSL::Cipher.new('AES-256-CBC')
    cipher.encrypt
    cipher.key = encryption_key
    
    encrypted = cipher.update(@access_token) + cipher.final
    self.encrypted_access_token = Base64.encode64(encrypted)
  end
  
  def encryption_key
    # Use environment variable or generate from secret
    key = ENV['ENCRYPTION_KEY'] || Rails.application.secret_key_base[0..31]
    Digest::SHA256.digest(key)[0..31]
  end
end
