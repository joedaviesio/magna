# Stripe Donations Setup Checklist

## 1. Create Product + Price

- [ ] Go to **Products** → **Add product**
- [ ] Name: "Bowen Public Donation"
- [ ] Create Price(s) — either:
  - One-time fixed amounts (e.g. $5, $10, $25) → gives a `price_xxx` ID for each
  - Or a single price with custom amount enabled
- [ ] Copy each `price_id`

## 2. Create Webhook Endpoint

- [ ] Go to **Developers** → **Webhooks** → **Add endpoint**
- [ ] URL: `https://your-production-domain.com/api/stripe/webhook`
- [ ] Select events:
  - `checkout.session.completed`
  - `payment_intent.succeeded` (optional)
- [ ] Copy the **Webhook Signing Secret** (`whsec_xxx`)

## 3. Env Vars

- [ ] `STRIPE_SECRET_KEY` — `sk_live_xxx`
- [ ] `STRIPE_PUBLISHABLE_KEY` — `pk_live_xxx`
- [ ] `STRIPE_WEBHOOK_SECRET` — `whsec_xxx`
- [ ] `STRIPE_PRICE_ID` — `price_xxx` (or multiple if tiered)

## 4. Local Testing

- [ ] Install Stripe CLI: `brew install stripe/stripe-cli/stripe`
- [ ] Run `stripe login`
- [ ] Forward webhooks: `stripe listen --forward-to localhost:8105/api/stripe/webhook`
- [ ] Use the local `whsec_xxx` for dev

## 5. Success / Cancel URLs

- [ ] Decide post-payment redirect (e.g. `https://bowenpublic.com?donated=true`)
- [ ] Decide cancel redirect (e.g. `https://bowenpublic.com`)
