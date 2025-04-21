-- Add storage_path column to images table
ALTER TABLE images 
ADD COLUMN storage_path VARCHAR(255);

-- Add dalle_url column to store the original URL
ALTER TABLE images 
ADD COLUMN dalle_url TEXT;
