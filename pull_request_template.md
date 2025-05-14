## 內容說明（必填）

請簡要列出此 PR 中完成的修改內容，建議使用條列式標記各項變更：

- feat: 新增查核工具 API
- fix: 修正 fakeNewsAgent 錯誤處理
- refactor: 重構 GM 評分模組邏輯
- chore: 加入 PR 模板

## 注意事項（如有）

- 說明需要 reviewer 特別注意的部分、潛在風險、非預期行為或尚未完成的項目。
- 若無可留空。

## Git Flow 檢查清單

- [ ] 本次 PR 為 `feat/xxx → main`，符合分支策略
- [ ] 已從 `main` 建立分支，並完成 rebase 至最新 `origin/main`
- [ ] 如有 conflict，已完整解決並使用 `--force-with-lease` 推送
- [ ] commit message 符合格式（如 `feat: ` / `fix: ` / `refactor: `）
- [ ] 已清理本地與遠端的分支（PR 合併後請刪除）

## PR 檢查清單

- [ ] 已通過本地測試，確認邏輯與功能正確
- [ ] PR 說明已填寫完整，包含「做了什麼」與「注意事項」
- [ ] 若有影響其他模組，已通知相關負責人
- [ ] 若涉及資料庫，已執行並驗證 Alembic migration
- [ ] 無多餘的除錯用 print 或註解
