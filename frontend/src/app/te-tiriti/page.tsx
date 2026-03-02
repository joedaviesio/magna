'use client';

import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function TeTiritiPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-3xl mx-auto px-6 py-12">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-slate-600 hover:text-slate-900 mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Bowen
        </Link>

        <h1 className="text-3xl font-semibold text-slate-900 mb-2">
          Bowen's Approach to Te Tiriti o Waitangi
        </h1>
        <p className="text-slate-500 mb-8">
          How Bowen handles Treaty of Waitangi matters in New Zealand law
        </p>

        <div className="prose prose-slate max-w-none">
          <section className="mb-12">
            <h2>From Possession to Ownership: Land Law and the Treaty in Colonial New Zealand</h2>
            <p className="text-sm text-slate-500 mb-4">
              Essay by Joe Davies, Founder of Bowen
            </p>

            <blockquote className="border-l-4 border-slate-300 pl-4 italic text-slate-600 my-6">
              "Land is much more than the sods of earth that comprise it... socially land gives us
              somewhere to live, somewhere to build a family, somewhere to be an active citizen,
              it provides the blank canvas against which we shape our lives and our businesses."
              <footer className="text-sm mt-2">— Chris Bevan</footer>
            </blockquote>

            <p>
              In light of this quote it is important to consider how this blank canvas, providing
              peace and opportunity for our lives, is ultimately regulated through its title legal
              system, in checks and balances, documentation and processes providing legitimacy to
              the symbolic wax and seal.
            </p>

            <h3>Two Systems of Title</h3>
            <p>
              Kevin Gray and Susan Francis Gray write that the idea of title relativity, rooted in
              possession of property or land, is a fundamental aspect of land and property law.
              This principle states that ownership persists as long as possession is maintained,
              valid against all but superior claims.
            </p>
            <p>
              Stuart Banner states that by distinguishing between "land" as the physical substance
              and "property" as the conceptual framework governing rights to use land, we can
              observe in colonial New Zealand the imposition of two divergent property systems by
              the British and the Māori on the same land.
            </p>

            <h3>Māori Land Rights Before 1840</h3>
            <p>
              John White writes that prior to European influence on New Zealand, Māori traditionally
              distributed property rights based on function rather than geography, assigning them
              to individuals and families. For example, one family might utilise the same tree for
              fowling, while another would gather berries from it.
            </p>
            <p>
              The Māori did not have a written language and their land was inherited not from
              individual to individual but rather the hapū or the greater iwi, and distributed
              amongst its resources by rangatira.
            </p>

            <h3>The Treaty and Pre-emption</h3>
            <p>
              New Zealand was born in 1840, as The Treaty of Waitangi was signed by 500 Chiefs and
              a representative of Her Majesty Queen Victoria. Article Two gave the Crown the
              exclusive right of pre-emption—the sole right to purchase lands from Māori.
            </p>
            <p>
              This was tested in 1847 when Governor George Grey brought <em>R v Symonds</em> to the
              Supreme Court. Chief Justice William Martin ruled that "the sole and absolute right
              of pre-emption from the aboriginal inhabitants vest in and can only be exercised by
              her Majesty, her Heirs and Successors."
            </p>

            <h3>The Native Land Court</h3>
            <p>
              The overhaul came in 1865 when The Native Land Court was established by the colonial
              government. The court began to assign individual titles to Māori land. James Belich
              states that in 1800, the Māori owned over 60 million acres of land; by 1911, they
              owned only 7 million, much of which was not productive land.
            </p>

            <h3>Wi Parata and "A Simple Nullity"</h3>
            <p>
              In 1877, Wi Parata, a prominent Māori farmer and political figure, challenged
              Bishop Octavius Hadfield over the Anglican Church's failure to fulfil an agreement
              with Ngāti Toa. The court dismissed the case, with Chief Justice James Prendergast
              deeming the Treaty irrelevant to domestic law:
            </p>
            <blockquote className="border-l-4 border-slate-300 pl-4 italic text-slate-600 my-6">
              "So far indeed as that instrument purported to cede sovereignty... it must be
              regarded as a simple nullity. No body politic existed capable of making cession
              of sovereignty, nor could the thing itself exist."
            </blockquote>
            <p>
              This position dominated NZ law for over a century before being overturned by
              modern Treaty jurisprudence, beginning with the Lands Case in 1987.
            </p>

            <h3>Conclusion</h3>
            <p>
              By the close of the nineteenth century, Māori found themselves stripped of the
              majority of their ancestral lands, along with their traditional land system of
              possession in use. An alternative framework for delineating land rights—that of
              title and ownership—had supplanted the old order.
            </p>
            <p>
              Recognising this history, it becomes evident that the legal framework governing
              land ownership plays a crucial role in shaping our societies. By exploring the
              historical evolution of land registration and the transition from possession-based
              to ownership-based titles, we gain valuable context for understanding New Zealand's
              legal jurisdiction—and why Te Tiriti remains central to it.
            </p>
          </section>

          <section className="mb-12 border-t border-slate-200 pt-12">
            <h2>How Bowen Handles Treaty Queries</h2>
            <p>
              Te Tiriti o Waitangi is foundational to New Zealand's legal system. It underpins our
              constitutional arrangements and increasingly permeates statute law across environmental,
              health, education, and governance domains. For a legal information tool like Bowen,
              handling Treaty matters requires particular care.
            </p>

            <h3>The Two Texts</h3>
            <p>
              Bowen recognises the material differences between the Māori and English texts of
              Te Tiriti. Article 2, for example, guarantees "tino rangatiratanga" in te reo Māori
              but "exclusive and undisturbed possession" in English—concepts that carry different
              weight and meaning.
            </p>

            <h3>Treaty Principles</h3>
            <p>
              Through case law, particularly the landmark <em>NZ Maori Council v Attorney-General</em> [1987]
              (the "Lands Case"), the courts have developed Treaty principles including:
            </p>
            <ul>
              <li><strong>Partnership</strong> — The Crown and Māori are partners requiring good faith</li>
              <li><strong>Active Protection</strong> — The Crown must actively protect Māori interests</li>
              <li><strong>Redress</strong> — Where breaches occur, the Crown should provide remedy</li>
            </ul>

            <h3>Treaty Clauses in Legislation</h3>
            <p>
              Many modern NZ Acts contain Treaty clauses. Bowen's database includes legislation like:
            </p>
            <ul>
              <li>Treaty of Waitangi Act 1975</li>
              <li>Te Ture Whenua Maori Act 1993</li>
              <li>Resource Management Act 1991 (s8 — Treaty principles)</li>
              <li>Conservation Act 1987 (s4 — give effect to Treaty principles)</li>
              <li>Various Treaty settlement Acts</li>
            </ul>

            <h3>Historical Context</h3>
            <p>
              Bowen draws on curated scholarly references to provide historical context, including
              the evolution from <em>Wi Parata v Bishop of Wellington</em> (1877)—which dismissed
              the Treaty as "a simple nullity"—to the modern recognition of Treaty principles as
              central to NZ law.
            </p>
          </section>

          <section className="mb-12">
            <h2>Ongoing Work</h2>
            <p>
              Bowen's approach to Treaty matters is evolving. We are continuously working to:
            </p>
            <ul>
              <li>Expand coverage of Treaty settlement legislation</li>
              <li>Incorporate Waitangi Tribunal findings</li>
              <li>Improve detection of Treaty-related queries</li>
              <li>Add scholarly references for historical context</li>
            </ul>
            <p>
              This is sensitive and important work. We welcome feedback from users, particularly
              those with expertise in Treaty jurisprudence and tikanga Māori.
            </p>
          </section>

          <section className="border-t border-slate-200 pt-8">
            <p className="text-sm text-slate-500">
              Bowen is a free public legal information tool. It provides information, not legal advice.
              For legal decisions involving Treaty matters, consult a qualified lawyer with expertise
              in this area.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
