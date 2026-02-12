/**
 * Format error messages from API responses
 * Handles both string errors and Pydantic validation error objects
 */
export const formatErrorMessage = (error) => {
  // If error is already a string, return it
  if (typeof error === 'string') {
    return error;
  }

  // Handle array of validation errors (Pydantic format)
  if (Array.isArray(error)) {
    return error.map(err => {
      if (typeof err === 'string') return err;
      
      // Format Pydantic validation error
      const field = err.loc ? err.loc.join(' -> ') : 'Field';
      const message = err.msg || 'Invalid value';
      return `${field}: ${message}`;
    }).join('; ');
  }

  // Handle single validation error object
  if (error && typeof error === 'object') {
    // Check if it's a Pydantic validation error
    if (error.msg && error.loc) {
      const field = error.loc.join(' -> ');
      return `${field}: ${error.msg}`;
    }

    // Check if it has a message property
    if (error.message) {
      return error.message;
    }

    // Check if it has a detail property
    if (error.detail) {
      return formatErrorMessage(error.detail);
    }

    // Try to stringify the object
    try {
      return JSON.stringify(error);
    } catch {
      return 'An error occurred';
    }
  }

  return 'An unexpected error occurred';
};

/**
 * Extract error message from axios error response
 */
export const getErrorMessage = (err, defaultMessage = 'An error occurred') => {
  // Check for response data detail
  if (err.response?.data?.detail) {
    return formatErrorMessage(err.response.data.detail);
  }

  // Check for response data message
  if (err.response?.data?.message) {
    return formatErrorMessage(err.response.data.message);
  }

  // Check for error message
  if (err.message) {
    return err.message;
  }

  return defaultMessage;
};
