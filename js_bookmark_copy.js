(() => {
  try {
    const clean = (s) => (s || "").replace(/\s+/g, " ").trim();

    const lines = document.body.innerText
      .split("\n")
      .map(clean)
      .filter(Boolean);

    const findBetween = (start, end) => {
      const startIndex = lines.findIndex(
        (x) => x.toLowerCase() === start.toLowerCase(),
      );
      if (startIndex === -1) return [];

      const endIndex = lines.findIndex(
        (x, i) => i > startIndex && x.toLowerCase() === end.toLowerCase(),
      );

      return endIndex === -1
        ? lines.slice(startIndex + 1)
        : lines.slice(startIndex + 1, endIndex);
    };

    const findLabeledValue = (label) => {
      for (const line of lines) {
        const m = line.match(new RegExp("^" + label + "\\s*:?\\s*(.+)$", "i"));
        if (m) return clean(m[1]);
      }
      return "";
    };

    const getHeaderTitleAndCompany = () => {
      // On this FINN page the main header appears as:
      // Business Analyst
      // Kongsberg Maritime
      // Frist ...
      // Ansettelsesform ...
      for (let i = 0; i < lines.length - 3; i++) {
        const a = lines[i];
        const b = lines[i + 1];
        const c = lines[i + 2];
        const d = lines[i + 3];

        const looksLikeMeta =
          c.startsWith("Frist") ||
          d.startsWith("Frist") ||
          c.startsWith("Ansettelsesform") ||
          d.startsWith("Ansettelsesform");

        if (
          a &&
          b &&
          a !== "Her er du" &&
          a !== "FINN" &&
          a !== "Legg til som favoritt." &&
          a !== "Video" &&
          a.length < 120 &&
          b.length < 120 &&
          !b.startsWith("Frist") &&
          !b.startsWith("Ansettelsesform") &&
          looksLikeMeta
        ) {
          return { title: a, company: b };
        }
      }

      return { title: "", company: "" };
    };

    const getSkills = () => {
      const skillstest = findBetween("Ferdigheter", "Om arbeidsgiveren")
        .filter((x) => x.toLowerCase() !== "ai-generert")
        .filter((x) => !x.includes("%"))
        .filter((x) => x !== "Se hvordan du matcher")
        .join(", ");
      return skillstest.split("Sektor")[0];
    };

    const getKeywords = () => {
      const testKeywords = clean(
        findBetween("Nøkkelord", "Spørsmål om stillingen").join(" "),
      );
      return testKeywords.split("Forrige bilde")[0];
    };

    const getFinnCode = () => {
      return (
        (location.href.match(/\/ad\/(\d+)/) || [])[1] ||
        (document.body.innerText.match(/FINN-kode\s*(\d+)/i) || [])[1] ||
        ""
      );
    };

    const header = getHeaderTitleAndCompany();

    const data = {
      Job_title: header.title,
      Company: header.company,
      Skills: getSkills(),
      Sector: findLabeledValue("Sektor"),
      Location: findLabeledValue("Sted"),
      Industry: findLabeledValue("Bransje"),
      Position: findLabeledValue("Stillingsfunksjon"),
      Keywords: getKeywords(),
      Finn_code: getFinnCode(),
    };

    const output = JSON.stringify(data, null, 2);
    console.log(output);

    navigator.clipboard
      .writeText(output)
      .then(() => alert("Copied to clipboard:\n\n" + output))
      .catch((err) => {
        console.error("Clipboard write failed:", err);
        alert("Output written to console. Clipboard copy failed.");
      });
  } catch (err) {
    console.error("Bookmarklet error:", err);
    alert("Script error: " + err.message);
  }
})();
