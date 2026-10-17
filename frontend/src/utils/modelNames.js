const diseaseModelNames = {
  diabetes: 'Logistic Regression',
  heart_disease: 'Logistic Regression',
  ckd: 'Random Forest',
  chronic_kidney_disease: 'Random Forest',
}

export function modelNameForDisease(diseaseId, fallback = 'Model') {
  return diseaseModelNames[diseaseId] || fallback || 'Model'
}
