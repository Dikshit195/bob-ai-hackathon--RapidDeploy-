# Problem Statement

## Background

Cold-chain and supply-chain logistics is one of the most time-critical sectors in modern commerce.
Perishable goods — dairy, frozen food, pharmaceuticals, fresh produce, and seafood — must be transported
within strict temperature bands at all times. A refrigerated truck carrying vaccines must hold 2–8 °C
for the entire journey; a freezer van delivering ice cream cannot drift above −15 °C even briefly.

India's logistics sector moves over ₹14 trillion worth of goods annually, with cold-chain capacity
growing at 15% per year. Fleet operators now deploy IoT temperature sensors in every reefer unit,
generating thousands of readings per day across hundreds of active shipments.

## The Problem

Despite this sensor coverage, operations teams are still flying blind. Three critical gaps persist:

**1. No unified real-time visibility.**
IoT sensor readings from different vehicles, carriers, and regions are stored in disconnected
systems — separate vendor portals, emailed CSV reports, or phone calls from drivers. There is no
single view showing all active shipments, their current temperatures, and live GPS positions at once.

**2. Temperature excursions are detected too late.**
When a reefer compressor fails or a door seal is broken, the temperature rises gradually.
By the time a driver notices or an alert email arrives, the excursion may have lasted 30–90 minutes —
long enough to violate pharmaceutical cold-chain regulations or spoil an entire load of ice cream.
The cost of a single undetected excursion on a pharma shipment can exceed ₹10 lakh in product loss
and regulatory penalties.

**3. Disruptions and delays are tracked in spreadsheets, not dashboards.**
Port congestion, vehicle breakdowns, bad weather on a highway corridor, and customs backlogs all
affect shipment ETAs — but each is tracked by a different team using a different tool. The operations
manager has no way to correlate a delayed shipment with the disruption event causing it, or to see
the overall impact score across all active disruptions at once.

## Who is Affected

The primary users experiencing this problem are:

- **Cold-chain operations managers** at FMCG and pharmaceutical companies who oversee 5–50 active
  shipments at any given time and are accountable for product quality on delivery.
- **Fleet coordinators** at logistics companies (BlueDart, Delhivery, DTDC, Ecom Express) who manage
  10–100 vehicles and need to know which are idle, which need maintenance, and which are carrying
  at-risk loads.
- **Quality assurance teams** in pharma and dairy who must document temperature compliance for
  regulatory audits and cannot do so without accurate, timestamped excursion records.

## Why It Matters

The consequences of poor cold-chain visibility are direct and quantifiable:

| Impact | Estimated Cost |
|---|---|
| Single pharma excursion (vaccine batch) | ₹5–15 lakh in product loss + potential regulatory fine |
| Undiscovered reefer failure (frozen goods) | ₹1–3 lakh per vehicle load |
| Fleet idle time (untracked) | ₹2,000–5,000 per hour per idle vehicle |
| Delayed disruption response | 2–4 hour cascading ETA delays across downstream shipments |

Beyond financial cost, delayed detection of temperature excursions in the pharmaceutical supply chain
is a patient safety issue — vaccines and insulin stored outside range may lose efficacy without any
visible sign of spoilage.

## Why Existing Solutions Fall Short

Current approaches used by most mid-sized logistics teams:

- **Vendor-specific IoT portals** — each sensor manufacturer provides its own portal with its own
  login. A fleet using three different sensor brands needs three browser tabs to get a complete picture.
- **Email/SMS alerts** — threshold breach notifications arrive minutes after the event, with no
  context about which shipment, which product, or how long the excursion has lasted.
- **Manual Excel tracking** — disruptions, delays, and fleet idle time are recorded in shared
  spreadsheets updated once or twice per day — not in real time.
- **Siloed fleet management systems** — vehicle location and fuel data is available, but not
  correlated with the IoT readings from the cargo being carried.

None of these tools answers the operations manager's core question:
**"Right now, which of my shipments is at risk, why, and what do I do about it?"**
