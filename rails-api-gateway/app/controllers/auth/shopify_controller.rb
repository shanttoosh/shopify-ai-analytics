module Auth
  class ShopifyController < ApplicationController
    def install
      shop = params[:shop]
      
      unless shop&.match?(/\A[a-zA-Z0-9][a-zA-Z0-9\-]*\.myshopify\.com\z/)
        return render json: { error: 'Invalid shop parameter' }, status: :bad_request
      end
      
      # Generate state for CSRF protection
      state = SecureRandom.hex(16)
      session[:shopify_state] = state
      session[:shop] = shop
      
      # Build OAuth URL
      scopes = ENV['SHOPIFY_SCOPES'] || 'read_products,read_orders'
      redirect_uri = ENV['SHOPIFY_CALLBACK_URL']
      client_id = ENV['SHOPIFY_API_KEY']
      
      auth_url = "https://#{shop}/admin/oauth/authorize?" + {
        client_id: client_id,
        scope: scopes,
        redirect_uri: redirect_uri,
        state: state
      }.to_query
      
      redirect_to auth_url, allow_other_host: true
    end
    
    def callback
      # Verify state
      unless params[:state] == session[:shopify_state]
        return render json: { error: 'Invalid state parameter' }, status: :forbidden
      end
      
      shop = session[:shop]
      code = params[:code]
      
      unless code
        return render json: { error: 'Authorization code missing' }, status: :bad_request
      end
      
      # Exchange code for access token
      begin
        response = HTTParty.post(
          "https://#{shop}/admin/oauth/access_token",
          body: {
            client_id: ENV['SHOPIFY_API_KEY'],
            client_secret: ENV['SHOPIFY_API_SECRET'],
            code: code
          }
        )
        
        if response.success?
          access_token = response.parsed_response['access_token']
          
          # Save to database with encryption
          store = Store.find_or_initialize_by(shop_domain: shop)
          store.access_token = access_token
          store.save!
          
          # Clean up session
          session.delete(:shopify_state)
          session.delete(:shop)
          
          render json: { 
            message: 'Successfully authenticated!', 
            shop: shop,
            note: 'You can now use /api/v1/questions endpoint'
          }
        else
          render json: { error: 'Failed to get access token' }, status: :bad_request
        end
      rescue => e
        Rails.logger.error "OAuth error: #{e.message}"
        render json: { error: 'Authentication failed', details: e.message }, status: :internal_server_error
      end
    end
  end
end
