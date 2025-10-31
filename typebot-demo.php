<?php
// Als er data is gepost, bouw de iframe URL
$iframe_url = null;
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  $base_url = 'https://typebot.co/faq-8hhmccv';
  $query_params = http_build_query([
    'transcript_url'     => $_POST['transcript'] ?? '',
    'chapters'           => $_POST['chapters'] ?? '',
    'guest'              => $_POST['guest'] ?? '',
    'guest_description'  => $_POST['guest_description'] ?? '',
    'forwho'             => $_POST['forwho'] ?? '',
  ]);
  $iframe_url = $base_url . '?' . $query_params;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Typebot Demo</title>
<style>
body {
  font-family: system-ui, sans-serif;
  margin: 2rem;
}
label {
  display:block;
  margin-top:1rem;
  font-weight:600;
}
textarea, input {
  width:100%;
  padding:0.5rem;
  border:1px solid #ccc;
  border-radius:4px;
  font-family:inherit;
}
button {
  margin-top:1.5rem;
  padding:0.75rem 1.5rem;
  background:#0077ff;
  color:white;
  border:none;
  border-radius:4px;
  cursor:pointer;
}
iframe {
  width:100%;
  height:600px;
  border:none;
  margin-top:2rem;
}
</style>
</head>
<body>

<h2>🧠 Typebot Test Form</h2>
<form method="post">
  <label>Transcript</label>
  <textarea name="transcript" rows="4" placeholder="Enter demo transcript"><?php echo htmlspecialchars($_POST['transcript'] ?? 'This is a demo transcript to test mobile behavior.'); ?></textarea>

  <label>Chapters</label>
  <input type="text" name="chapters" value="<?php echo htmlspecialchars($_POST['chapters'] ?? 'Introduction - Vision - Guest Experience'); ?>">

  <label>Guest</label>
  <input type="text" name="guest" value="<?php echo htmlspecialchars($_POST['guest'] ?? 'John Doe'); ?>">

  <label>Guest Description</label>
  <input type="text" name="guest_description" value="<?php echo htmlspecialchars($_POST['guest_description'] ?? 'General Manager at Grand Plaza Hotels'); ?>">

  <label>For Who</label>
  <input type="text" name="forwho" value="<?php echo htmlspecialchars($_POST['forwho'] ?? 'Hoteliers and hospitality leaders'); ?>">

  <button type="submit">Generate Typebot</button>
</form>

<?php if ($iframe_url): ?>
  <iframe src="<?php echo htmlspecialchars($iframe_url); ?>" allow="clipboard-read; clipboard-write"></iframe>
<?php endif; ?>

</body>
</html>
