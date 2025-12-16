class CreateStores < ActiveRecord::Migration[8.1]
  def change
    create_table :stores do |t|
      t.string :shop_domain, null: false
      t.text :encrypted_access_token

      t.timestamps
    end
    
    add_index :stores, :shop_domain, unique: true
  end
end
