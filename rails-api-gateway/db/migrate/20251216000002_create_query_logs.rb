class CreateQueryLogs < ActiveRecord::Migration[8.1]
  def change
    create_table :query_logs do |t|
      t.string :store_id
      t.text :question
      t.text :response

      t.timestamps
    end
    
    add_index :query_logs, :store_id
    add_index :query_logs, :created_at
  end
end
