class HealthController < ApplicationController
  def show
    render json: {
      status: 'ok',
      service: 'rails-api-gateway',
      rails_version: Rails::VERSION::STRING,
      timestamp: Time.current.iso8601
    }
  end
end
