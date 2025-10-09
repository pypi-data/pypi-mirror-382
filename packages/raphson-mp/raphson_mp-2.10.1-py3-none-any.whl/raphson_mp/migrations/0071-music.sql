-- remove audio blobs from before loudness change
DELETE FROM blob WHERE blobtype IN ('audio_webm_opus_high', 'audio_webm_opus_low', 'audio_mp3_with_metadata');
