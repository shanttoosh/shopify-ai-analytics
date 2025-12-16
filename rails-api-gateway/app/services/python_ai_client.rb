require 'httparty'

class PythonAIClient
  include HTTParty
  base_uri ENV['PYTHON_AI_SERVICE_URL'] || 'http://localhost:8000'
  
  def self.analyze_question(store_id:, question:, access_token: nil, use_mock: true)
    response = post('/analyze', {
      body: {
        store_id: store_id,
        question: question,
        access_token: access_token,
        use_mock: use_mock
      }.to_json,
      headers: {
        'Content-Type' => 'application/json'
      },
      timeout: 30
    })
    
    if response.success?
      JSON.parse(response.body)
    else
      raise "Python AI Service error: #{response.code} - #{response.message}"
    end
  rescue Errno::ECONNREFUSED, Net::OpenTimeout => e
    raise "Cannot connect to Python AI service at #{base_uri}. Is it running?"
  end
  
  def self.health_check
    response = get('/health', timeout: 5)
    response.success?
  rescue
    false
  end
end
