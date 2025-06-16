// src/App.js
import React from "react";
import {
  SearchProvider,
  SearchBox,
  Results,
  PagingInfo,
  Paging
} from "@elastic/react-search-ui";
import { config } from "./search-config";
import "@elastic/react-search-ui-views/lib/styles/styles.css";

export default function App() {
  return (
    <SearchProvider config={config}>
      <div className="container">
        <header>
          <h1>CV Transcriptions Search</h1>
          <SearchBox searchAsYouType debounceLength={300} />
        </header>

        <main>
          <PagingInfo />

          <Results
            view="table"
            titleField="generated_text"
            fields={[
              "generated_text",
              "duration",
              "age",
              "gender",
              "accent"
            ]}
          />

          <Paging />
        </main>

        <footer>
          <p>Project done by Cleon.</p>
        </footer>
      </div>
    </SearchProvider>
  );
}