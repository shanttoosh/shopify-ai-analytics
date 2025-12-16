Rails.application.routes.draw do
  # Health check
  get "health", to: "health#show"
  
  # API namespace
  namespace :api do
    namespace :v1 do
      post "questions", to: "questions#create"
    end
  end
  
  # Shopify OAuth
  namespace :auth do
    get "shopify", to: "shopify#install"
    get "shopify/callback", to: "shopify#callback"
  end
  
  # Root route
  root to: proc { [200, { "Content-Type" => "application/json" }, [{ message: "Shopify Analytics API Gateway (Rails)" }.to_json]] }
end
