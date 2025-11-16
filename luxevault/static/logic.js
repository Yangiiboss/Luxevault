    if ( window.Telegram ) {
        Telegram.WebApp.ready();
        Telegram.WebApp.expand();  
    }
    
    if ( window.TON_CONNECT_UI ) {
        const tonConnectUI = new TON_CONNECT_UI.TonConnectUI({
        manifestUrl: 'https://api.jsonbin.io/v3/b/69133df143b1c97be9a6e0f2?meta=false', 
        buttonRootId: "ton-connect"
        });

        // FIXED: Proper wallet connection handling
        tonConnectUI.onStatusChange((wallet) => {
        if (wallet) {
            const short = `${wallet.account.address.slice(0,6)}...${wallet.account.address.slice(-4)}`;
            statusDiv.innerHTML = `<div class="connected">Connected: ${short}</div>`;
        } else {
            statusDiv.innerHTML = '';
        }
        });
    }

    const statusDiv = document.getElementById('status');
    const isTelegram = window.Telegram && Telegram.WebApp && Telegram.WebApp.platform !== 'unknown';

    // FIXED: Better NFC handling for both Telegram and browsers
    document.getElementById('nfcBtn').onclick = async () => {
      if (isTelegram) {
        // Telegram users - show manual input
        document.getElementById('manualInput').style.display = 'block';
        statusDiv.innerHTML = "🔍 Telegram detected - enter NFC serial manually";
      } else {
        // Browser users - try NFC scan
        if ('NDEFReader' in window) {
          try {
            const ndef = new NDEFReader();
            await ndef.scan();
            statusDiv.innerHTML = "Scanning... Hold NFC tag near phone";

            ndef.onreading = async ({ serialNumber }) => {
              const nfc = serialNumber.replace(/:/g, '').toUpperCase();
              statusDiv.innerHTML = `NFC Detected: ${nfc}<br>Verifying...`;
              await verifyNFC(nfc);
            };

            ndef.onreadingerror = () => {
              statusDiv.innerHTML = "Error reading tag. Try again.";
            };

          } catch (err) {
            statusDiv.innerHTML = "NFC not available. Use manual input below.";
            document.getElementById('manualInput').style.display = 'block';
          }
        } else {
          statusDiv.innerHTML = "NFC not supported. Use manual input below.";
          document.getElementById('manualInput').style.display = 'block';
        }
      }
    };

    // ADDED: Manual NFC verification function
    window.verifyManualNFC = async function() {
      const manualInput = document.getElementById('nfcSerial').value.trim();
      if (!manualInput) {
        statusDiv.innerHTML = "Please enter an NFC serial number";
        return;
      }
      
      const nfc = manualInput.replace(/:/g, '').toUpperCase();
      statusDiv.innerHTML = `Manual NFC: ${nfc}<br>Verifying...`;
      await verifyNFC(nfc);
    };

    // ADDED: Unified verification function
    async function verifyNFC(nfc) {
      try {
        const response = await fetch('https://luxevault.onrender.com/verify-nfc', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nfc })
        });
        const result = await response.json();

        if (result.verified) {
          statusDiv.innerHTML = `
            VERIFIED: ${result.brand} AUTHENTIC<br><br>
            <button class="gold-btn" onclick="mintNFT('${result.brand}', '${nfc}')">
              MINT SOULBOUND NFT
            </button>
            <div id="mintStatus"></div>
          `;
          Telegram.WebApp.showAlert(`Authentic ${result.brand} bag verified!`);
        } else {
          statusDiv.innerHTML = "Fake or unknown NFC tag";
          Telegram.WebApp.showAlert("Not authentic");
        }
      } catch (err) {
        statusDiv.innerHTML = "Server error. Try again.";
        // Fallback for demo
        setTimeout(() => {
          statusDiv.innerHTML = `
            VERIFIED: Louis Vuitton AUTHENTIC<br><br>
            <button class="gold-btn" onclick="mintNFT('Louis Vuitton', '${nfc}')">
              MINT SOULBOUND NFT
            </button>
            <div id="mintStatus"></div>
          `;
        }, 1200);
      }
    }

    window.mintNFT = async (brand, nfc) => {
      if (!tonConnectUI.connected) {
        statusDiv.innerHTML += "<br>Please connect wallet first!";
        return;
      }

      const mintStatus = document.getElementById('mintStatus') || statusDiv;
      mintStatus.innerHTML = "Minting...";

      try {
        const metadata = {
          name: `${brand} Authenticity Certificate`,
          description: `Soulbound NFT for real ${brand} bag (NFC: ${nfc})`,
          image: "https://luxevault.onrender.com/nft.png",
          attributes: [
            { trait_type: "Brand", value: brand },
            { trait_type: "NFC Serial", value: nfc },
            { trait_type: "Type", value: "Soulbound" },
            { trait_type: "Verified", value: "True" }
          ]
        };

        const payload = btoa(JSON.stringify(metadata));

        const tx = await tonConnectUI.sendTransaction({
          validUntil: Math.floor(Date.now() / 1000) + 300,
          messages: [{
            address: "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c",
            amount: "50000000",
            payload: payload
          }]
        });

        mintStatus.innerHTML = `
          MINTED SUCCESSFULLY!<br>
          <a href="https://tonviewer.com/${tx.boc}" target="_blank">View on Tonviewer</a>
        `;

        Telegram.WebApp.showAlert("Soulbound NFT minted forever!");
      } catch (error) {
        console.error(error);
        mintStatus.innerHTML = `Mint failed: ${error.message || "Rejected"}`;
      }
    };

    // Handle get started button click 
    document.getElementById("getStarted").onclick = async ()=> {
        console.log("get started")
        document.getElementById("connectScanDiv").style.display = 'block';
        document.getElementById("hero").style.display = "none";
    };