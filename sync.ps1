param(
    [string]$Message = "Update SHIFT game features and assets"
)

Write-Host "🚀 Syncing changes to GitHub (https://github.com/Snigdha-0210/Shift)..." -ForegroundColor Cyan
git add .
$changes = git status --porcelain
if (-not $changes) {
    Write-Host "✅ Working tree clean. No new changes to push." -ForegroundColor Green
} else {
    git commit -m "$Message"
    git push origin main
    Write-Host "🎉 Successfully pushed latest updates to GitHub!" -ForegroundColor Green
}
