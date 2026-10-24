export function firstFieldError(data, fallback) {
  if (!data || typeof data !== 'object') {
    return fallback;
  }
  const preferred = [
    'email',
    'username',
    'password',
    'password_confirm',
    'name',
    'title',
    'description',
    'content',
    'non_field_errors',
    'detail',
    'message',
  ];
  const keys = [...preferred, ...Object.keys(data)];
  const seen = new Set();
  for (const key of keys) {
    if (seen.has(key) || key === 'error') {
      continue;
    }
    seen.add(key);
    const value = data[key];
    if (typeof value === 'string' && value.trim()) {
      return value;
    }
    if (Array.isArray(value)) {
      const text = value.find((item) => typeof item === 'string' && item.trim());
      if (text) {
        return text;
      }
    }
  }
  return fallback;
}
