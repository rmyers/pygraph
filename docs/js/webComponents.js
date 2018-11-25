import {LitElement, html} from 'https://unpkg.com/@polymer/lit-element@0.6.3/lit-element.js?module';

class MyElement extends LitElement {

  static get properties() {
    return {
      whales: { type: Number}
    };
  }

  clickHandler() {
    this.whales++;
  }

  // Render method should return a `TemplateResult` using the provided lit-html `html` tag function
  render() {
    return html`
      <style>
        :host {
          display: block;
        }
        :host([hidden]) {
          display: none;
        }
      </style>
      <div>Whales: ${'🐳'.repeat(this.whales)}</div>
      <button @click="${(event) => this.clickHandler(event)}">Click Me to Whale it Up!</button>
      <slot></slot>
    `;
  }

}
customElements.define('my-element', MyElement);
