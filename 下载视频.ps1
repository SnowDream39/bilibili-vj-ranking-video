yt-dlp -a urls.txt `
  -f "bv*[height<=480][vcodec^=avc]+ba/bv*[height<=480][vcodec*=hev]+ba" `
  --playlist-items 1 `
  -o "./视频/%(webpage_url_basename)s.%(ext)s"  `
  --cookies cookies.txt `
  -N 5