import ElasticSearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";

const ES_HOST =
  process.env.REACT_APP_ES_HOST ||
  (window.location.protocol + "//" + window.location.hostname + ":9200");

const connector = new ElasticSearchAPIConnector({
  host: ES_HOST,
  index: "cv-transcriptions",
  cacheResponses: false
});

export const config = {
  apiConnector: connector,

  searchQuery: {
    // <-- OBJECT form, {} means default weight = 1
    search_fields: {
      generated_text: {},   // analysed text
      gender: {},           // text
      accent: {}            // text
    },

    result_fields: {
      generated_text: {
        snippet: { size: 300, fallback: true },
        raw: {}
      },
      duration: { raw: {} },
      age:      { raw: {} },
      gender:   { raw: {} },
      accent:   { raw: {} }
    }
  }
};
