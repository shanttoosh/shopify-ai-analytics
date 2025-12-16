module Api
  module V1
    class QuestionsController < ApplicationController
      def create
        # Validate input
        unless params[:store_id].present? && params[:question].present?
          return render json: { error: 'store_id and question are required' }, status: :bad_request
        end

        store_id = params[:store_id]
        question = params[:question]
        
        # Check if using mock data
        use_mock = ENV['USE_MOCK_DATA'] == 'true'
        
        # Get access token if not in mock mode
        access_token = nil
        unless use_mock
          store = Store.find_by(shop_domain: store_id)
          unless store
            return render json: { error: 'Store not found. Please authenticate first via /auth/shopify' }, status: :not_found
          end
          access_token = store.decrypted_access_token
        end
        
        # Call Python AI service
        begin
          ai_response = PythonAIClient.analyze_question(
            store_id: store_id,
            question: question,
            access_token: access_token,
            use_mock: use_mock
          )
          
          # Log query (optional)
          if ENV['ENABLE_QUERY_LOGS'] == 'true'
            QueryLog.create(
              store_id: store_id,
              question: question,
              response: ai_response.to_json
            )
          end
          
          render json: ai_response
        rescue => e
          Rails.logger.error "Error calling Python AI service: #{e.message}"
          render json: { error: 'Failed to process question', details: e.message }, status: :internal_server_error
        end
      end
    end
  end
end
