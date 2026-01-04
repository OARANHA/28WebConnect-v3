/// <reference types="react" />
/// <reference types="react-dom" />

declare global {
  namespace JSX {
    interface IntrinsicElements {
      div: React.DetailedHTMLProps<HTMLDivElement>;
      h1: React.DetailedHTMLProps<HTMLHeadingElement>;
      h2: React.DetailedHTMLProps<HTMLHeadingElement>;
      h3: React.DetailedHTMLProps<HTMLHeadingElement>;
      p: React.DetailedHTMLProps<HTMLParagraphElement>;
      span: React.DetailedHTMLProps<HTMLSpanElement>;
      button: React.DetailedHTMLProps<HTMLButtonElement>;
      img: React.DetailedHTMLProps<HTMLImageElement>;
      input: React.DetailedHTMLProps<HTMLInputElement>;
      label: React.DetailedHTMLProps<HTMLLabelElement>;
    }
  }
}
