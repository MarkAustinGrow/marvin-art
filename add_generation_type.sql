-- Add generation_type column to images table
ALTER TABLE images 
ADD COLUMN generation_type VARCHAR(10) DEFAULT 'auto' NOT NULL;

-- Update existing records to have 'auto' as their generation type
UPDATE images SET generation_type = 'auto';
