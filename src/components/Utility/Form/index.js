// Form serialization & validation utility
export const serializeForm = (formEl) => Object.fromEntries(new FormData(formEl));
