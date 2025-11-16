/**
 * API Client
 */

export const API = {
  /**
   * Make API call
   */
  async call(endpoint, method = "GET", body = null) {
    try {
      const options = {
        method,
        headers: { "Content-Type": "application/json" },
      };

      if (body) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(`/api/${endpoint}`, options);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Request failed");
      }

      return data;
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  },

  // Convenience methods
  get(endpoint) {
    return this.call(endpoint, "GET");
  },

  post(endpoint, body) {
    return this.call(endpoint, "POST", body);
  },
};
