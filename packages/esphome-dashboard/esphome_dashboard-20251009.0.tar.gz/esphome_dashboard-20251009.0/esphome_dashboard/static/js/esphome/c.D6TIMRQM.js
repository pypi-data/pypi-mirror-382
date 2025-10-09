import{D as o,E as t,r as e,_ as i,e as s,t as a,n as r,s as n,x as d,a1 as l,a2 as c}from"./index-BqvzQUql.js";import"./c.DDud9Ha3.js";import"./c.BqpeYcfD.js";import{m as p}from"./c.CBn2Xi0o.js";import"./c.DFrPKrhG.js";import"./c.Bu3X69fr.js";import"./c.4lF_hUsV.js";let m=class extends n{render(){let o,t;return o="What version do you want to download?",t=d`
      ${this._error?d`<div class="error">${this._error}</div>`:""}
      ${this._downloadTypes?d`
            ${this._downloadTypes.map((o=>d`
                <mwc-list-item
                  twoline
                  hasMeta
                  dialogAction="close"
                  @click=${()=>this._handleDownload(o)}
                >
                  <span>${o.title}</span>
                  <span slot="secondary">${o.description}</span>
                  ${p}
                </mwc-list-item>
              `))}
          `:d`<div>Checking files to download...</div>`}
    `,d`
      <mwc-dialog open heading=${"What version do you want to download?"} scrimClickAction>
        ${t}
        ${this.platformSupportsWebSerial?d`
              <a
                href="https://web.esphome.io"
                target="_blank"
                rel="noopener noreferrer"
                class="bottom-left"
                >Open ESPHome Web</a
              >
            `:""}

        <mwc-button
          no-attention
          slot="primaryAction"
          dialogAction="close"
          label="Cancel"
        ></mwc-button>
      </mwc-dialog>
    `}firstUpdated(o){super.firstUpdated(o),l(this.configuration).then((o=>{if(1==o.length)return this._handleDownload(o[0]),void this._close();this._downloadTypes=o})).catch((o=>{this._error=o.message||o}))}_handleDownload(o){const t=document.createElement("a");t.download=o.download,t.href=c(this.configuration,o),document.body.appendChild(t),t.click(),t.remove()}_close(){this.shadowRoot.querySelector("mwc-dialog").close()}};m.styles=[o,t,e`
      mwc-list-item {
        margin: 0 -20px;
      }
    `],i([s()],m.prototype,"configuration",void 0),i([s()],m.prototype,"platformSupportsWebSerial",void 0),i([a()],m.prototype,"_error",void 0),i([a()],m.prototype,"_downloadTypes",void 0),m=i([r("esphome-download-type-dialog")],m);
//# sourceMappingURL=c.D6TIMRQM.js.map
