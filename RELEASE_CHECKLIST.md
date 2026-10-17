# HealthSense Release Checklist

Audit date: 2026-09-08

## Required project content

- [x] Backend source present under `backend/`
- [x] Frontend source present under `frontend/src/`
- [x] Diabetes trained `research_v1` artifact present at `backend/ml/models/diabetes/model_bundle.joblib`
- [x] Heart Disease trained `research_v1` artifact present at `backend/ml/models/heart/model_bundle.joblib`
- [x] CKD trained `research_v1` artifact present at `backend/ml/models/ckd/model_bundle.joblib`
- [x] Heart and CKD original datasets preserved locally
- [ ] Diabetes original CSV included locally: training uses the remote Plotly URL and `backend/datasets/diabetes/original/` contains only `.gitkeep`
- [x] Dataset documentation present, including CKD source notes and model metadata
- [x] ML experiment/evaluation documentation present
- [x] Research documentation present
- [x] Backend/database configuration source present
- [x] `frontend/package.json` present
- [x] `frontend/package-lock.json` present
- [x] `backend/requirements.txt` present
- [x] Root `README.md` present
- [x] `backend/.env.example` present with placeholders only

## Safety and release hygiene

- [x] No real secret values copied into release documentation
- [ ] Verify `backend/.env` is excluded from the ZIP
- [ ] Verify no `frontend/node_modules/` is included
- [ ] Verify no root `.venv/` is included
- [ ] Verify no `backend/.venv/` is included if created later
- [ ] Verify no `__pycache__/` directories are included
- [ ] Verify no `*.pyc` files are included
- [ ] Verify no unnecessary generated `frontend/dist/` build is included
- [ ] Verify temporary logs, editor metadata, and OS cache files are excluded
- [ ] Exclude `.git/` unless Git history is intentionally required
- [ ] Exclude the local `backend/healthsense.db` unless the handoff intentionally includes its records; a fresh database is generated on startup

## Verification

- [x] Application startup instructions were verified against the actual commands and ports
- [x] Backend compilation passed during final verification
- [x] Frontend production build passed during final verification
- [x] All three production model bundles loaded during final verification
- [x] All three prediction endpoints returned successfully during final verification
- [x] Registration, login, protected routes, history, and invalid authentication were verified
- [ ] Fresh-machine setup should be tested after extracting the final ZIP
- [ ] Confirm whether a local Diabetes CSV must be added for the researcher's offline reproduction needs
- [ ] Final release is reproducible for normal prediction use
- [ ] Full offline retraining reproduction is complete: blocked until the remote Diabetes CSV is included or separately archived
