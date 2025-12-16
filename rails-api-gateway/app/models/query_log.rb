class QueryLog < ApplicationRecord
  validates :store_id, :question, presence: true
end
