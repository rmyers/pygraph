import {LitElement, html} from 'https://unpkg.com/@polymer/lit-element@0.6.3/lit-element.js?module';

var graph = graphql("http://localhost:8000/api/v2/graphql")

class MyElement extends LitElement {

  static get properties() {
    return {
      whales: { type: Number}
    };
  }

  callit() {
    console.log('callin it');
    return graph(`query ($username: String) {
        getCommitCalendar(username: $username) {
          start
          end
        }
      }`
    )();
  }

  clickHandler() {
    this.whales++;
    this.callit({username: 'rmyers'});
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
