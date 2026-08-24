import { useEffect, useState } from "react"

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from "recharts"

import "./App.css"


const API_URL = "http://127.0.0.1:8000"


const CHART_COLORS = [
  "#7c5cff",
  "#00d4ff",
  "#ff6b8a",
  "#ffb84d",
  "#4ade80"
]


function App() {

  // =========================================================
  // PAYMENT FORM
  // =========================================================

  const [amount, setAmount] = useState(5000)

  const [paymentMethod, setPaymentMethod] =
    useState("UPI")

  const [bank, setBank] =
    useState("SBI")

  const [gateway, setGateway] =
    useState("Gateway_A")


  // =========================================================
  // PAYMENT RESULT
  // =========================================================

  const [result, setResult] =
    useState(null)

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState("")


  // =========================================================
  // ANALYTICS
  // =========================================================

  const [overview, setOverview] =
    useState(null)

  const [gateways, setGateways] =
    useState({})

  const [failures, setFailures] =
    useState([])

  const [analyticsLoading, setAnalyticsLoading] =
    useState(false)


  // =========================================================
  // RECOVERY ANALYTICS
  // =========================================================

  const [recoveryAnalytics, setRecoveryAnalytics] =
    useState(null)


  // =========================================================
  // TRANSACTION HISTORY
  // =========================================================

  const [transactions, setTransactions] =
    useState([])


  // =========================================================
  // REFRESH ANALYTICS
  // =========================================================

  const [refreshAnalytics, setRefreshAnalytics] =
    useState(0)


  // =========================================================
  // STATUS HELPERS
  // =========================================================

  const getStatusClass = (status) => {

    if (!status) {
      return ""
    }

    return status
      .toLowerCase()
      .replaceAll(" ", "-")
  }


  const formatStatus = (status) => {

    if (!status) {
      return "UNKNOWN"
    }

    return status.toUpperCase()
  }


  // =========================================================
  // LOAD ANALYTICS
  // =========================================================

  useEffect(() => {

    const fetchAnalytics = async () => {

      setAnalyticsLoading(true)

      try {

        const [
          overviewResponse,
          gatewayResponse,
          failureResponse,
          recoveryResponse,
          transactionResponse
        ] = await Promise.all([

          fetch(
            `${API_URL}/analytics/overview`
          ),

          fetch(
            `${API_URL}/analytics/gateways`
          ),

          fetch(
            `${API_URL}/analytics/failures`
          ),

          fetch(
            `${API_URL}/analytics/recovery`
          ),

          fetch(
            `${API_URL}/analytics/transactions`
          )

        ])


        if (
          !overviewResponse.ok ||
          !gatewayResponse.ok ||
          !failureResponse.ok ||
          !recoveryResponse.ok ||
          !transactionResponse.ok
        ) {

          throw new Error(
            "Analytics request failed"
          )

        }


        const overviewData =
          await overviewResponse.json()

        const gatewayData =
          await gatewayResponse.json()

        const failureData =
          await failureResponse.json()

        const recoveryData =
          await recoveryResponse.json()

        const transactionData =
          await transactionResponse.json()


        setOverview(
          overviewData
        )

        setGateways(
          gatewayData
        )

        setFailures(
          failureData.failure_reasons || []
        )

        setRecoveryAnalytics(
          recoveryData
        )

        setTransactions(
          transactionData.transactions || []
        )

      } catch (err) {

        console.error(
          "Analytics error:",
          err
        )

      } finally {

        setAnalyticsLoading(false)

      }

    }


    fetchAnalytics()

  }, [refreshAnalytics])


  // =========================================================
  // PROCESS PAYMENT
  // =========================================================

  const processPayment = async () => {

    setLoading(true)

    setError("")

    setResult(null)


    try {

      const response = await fetch(
        `${API_URL}/payments/`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({

            amount: Number(amount),

            payment_method:
              paymentMethod,

            bank:
              bank,

            gateway:
              gateway

          })
        }
      )


      if (!response.ok) {

        throw new Error(
          "Payment request failed"
        )

      }


      const data =
        await response.json()


      setResult(data)


      // Refresh dashboard
      // after payment

      setRefreshAnalytics(
        previous => previous + 1
      )


    } catch (err) {

      console.error(err)

      setError(
        "Unable to connect to the payment backend. Make sure FastAPI is running."
      )

    } finally {

      setLoading(false)

    }

  }


  // =========================================================
  // GATEWAY CHART DATA
  // =========================================================

  const gatewayChartData =
    Object.entries(
      gateways || {}
    ).map(
      ([gatewayName, data]) => ({

        gateway:
          gatewayName.replace(
            "_",
            " "
          ),

        successRate:
          data?.success_rate_percent ?? 0

      })
    )


  // =========================================================
  // FAILURE CHART DATA
  // =========================================================

  const failureChartData =
    (failures || []).map(
      (item) => ({

        name:
          item.failure_reason,

        value:
          item.count

      })
    )


  // =========================================================
  // RECOVERY CHART DATA
  // =========================================================

  const recoveryChartData = [

    {
      name: "Attempts",

      value:
        recoveryAnalytics?.total_attempts ?? 0
    },

    {
      name: "Failed",

      value:
        recoveryAnalytics?.failed_attempts ?? 0
    },

    {
      name: "Successful",

      value:
        recoveryAnalytics?.successful_attempts ?? 0
    },

    {
      name: "Recovered",

      value:
        recoveryAnalytics?.recovered_transactions ?? 0
    }

  ]


  // =========================================================
  // RENDER
  // =========================================================

  return (

    <div className="app">


      {/* =====================================================
          HEADER
      ===================================================== */}

      <header className="header">

        <div>

          <h1>
            AI Payment Reliability
          </h1>

          <p>
            Intelligent payment failure analysis & recovery
          </p>

        </div>


        <div className="status">

          <span className="status-dot"></span>

          Backend Online

        </div>

      </header>



      {/* =====================================================
          KPI CARDS
      ===================================================== */}

      <section className="stats-grid">


        {/* TOTAL TRANSACTIONS */}

        <div className="card stat-card">

          <span>
            Total Transactions
          </span>

          <h2>

            {overview
              ? overview.total_transactions
                  .toLocaleString()

              : analyticsLoading
                ? "..."

                : "0"
            }

          </h2>

          <small>
            Transactions analyzed
          </small>

        </div>



        {/* SUCCESS RATE */}

        <div className="card stat-card">

          <span>
            Success Rate
          </span>

          <h2>

            {overview
              ? `${overview.success_rate_percent}%`

              : analyticsLoading
                ? "..."

                : "0%"
            }

          </h2>

          <small>

            {overview
              ? `${overview.successful_transactions.toLocaleString()} successful`

              : "Loading..."
            }

          </small>

        </div>



        {/* FAILURE RATE */}

        <div className="card stat-card">

          <span>
            Failure Rate
          </span>

          <h2>

            {overview
              ? `${overview.failure_rate_percent}%`

              : analyticsLoading
                ? "..."

                : "0%"
            }

          </h2>

          <small>

            {overview
              ? `${overview.failed_transactions.toLocaleString()} failed`

              : "Loading..."
            }

          </small>

        </div>



        {/* RECOVERY SUCCESS */}

        <div className="card stat-card">

          <span>
            Recovery Success
          </span>

          <h2>

            {recoveryAnalytics
              ? `${recoveryAnalytics.recovery_success_rate_percent}%`

              : analyticsLoading
                ? "..."

                : "0%"
            }

          </h2>

          <small>

            {recoveryAnalytics
              ? `${recoveryAnalytics.recovered_transactions} transactions recovered`

              : "Loading..."
            }

          </small>

        </div>


      </section>



      {/* =====================================================
          TEST PAYMENT
      ===================================================== */}

      <section className="main-grid">


        <div className="card">

          <h2>
            Test Payment
          </h2>

          <p className="description">

            Simulate a payment and let the AI analyze
            and recover it.

          </p>


          <div className="form-grid">


            {/* AMOUNT */}

            <div>

              <label>
                Amount
              </label>

              <input
                type="number"
                value={amount}
                onChange={(e) =>
                  setAmount(e.target.value)
                }
              />

            </div>



            {/* PAYMENT METHOD */}

            <div>

              <label>
                Payment Method
              </label>

              <select
                value={paymentMethod}
                onChange={(e) =>
                  setPaymentMethod(
                    e.target.value
                  )
                }
              >

                <option value="UPI">
                  UPI
                </option>

                <option value="CARD">
                  CARD
                </option>

                <option value="NET_BANKING">
                  NET_BANKING
                </option>

                <option value="WALLET">
                  WALLET
                </option>

              </select>

            </div>



            {/* BANK */}

            <div>

              <label>
                Bank
              </label>

              <select
                value={bank}
                onChange={(e) =>
                  setBank(
                    e.target.value
                  )
                }
              >

                <option value="SBI">
                  SBI
                </option>

                <option value="HDFC">
                  HDFC
                </option>

                <option value="ICICI">
                  ICICI
                </option>

                <option value="AXIS">
                  AXIS
                </option>

                <option value="KOTAK">
                  KOTAK
                </option>

              </select>

            </div>



            {/* GATEWAY */}

            <div>

              <label>
                Gateway
              </label>

              <select
                value={gateway}
                onChange={(e) =>
                  setGateway(
                    e.target.value
                  )
                }
              >

                <option value="Gateway_A">
                  Gateway_A
                </option>

                <option value="Gateway_B">
                  Gateway_B
                </option>

                <option value="Gateway_C">
                  Gateway_C
                </option>

              </select>

            </div>


          </div>



          <button
            className="primary-btn"
            onClick={processPayment}
            disabled={loading}
          >

            {loading
              ? "⏳ Processing..."

              : "⚡ Process Payment"
            }

          </button>



          {error && (

            <div className="ai-placeholder">

              <p>
                ❌ {error}
              </p>

            </div>

          )}

        </div>


      </section>



      {/* =====================================================
          FAILURE ANALYSIS
      ===================================================== */}

      <section className="card">

        <h2>
          Failure Analysis
        </h2>


        <div className="failure-grid">

          {failures.length > 0 ? (

            failures.map(
              (failure) => (

                <div
                  className="failure-item"
                  key={
                    failure.failure_reason
                  }
                >

                  <span>
                    {failure.failure_reason}
                  </span>

                  <strong>
                    {failure.count.toLocaleString()}
                  </strong>

                </div>

              )
            )

          ) : (

            <div className="ai-placeholder">

              <p>

                {analyticsLoading
                  ? "Loading failure analysis..."

                  : "No failure data available."
                }

              </p>

            </div>

          )}

        </div>

      </section>



      {/* =====================================================
          RECOVERY ANALYTICS
      ===================================================== */}

      <section className="card">

        <h2>
          Recovery Analytics
        </h2>


        <div className="failure-grid">


          <div className="failure-item">

            <span>
              Total Attempts
            </span>

            <strong>
              {recoveryAnalytics?.total_attempts ?? 0}
            </strong>

          </div>



          <div className="failure-item">

            <span>
              Failed Attempts
            </span>

            <strong>
              {recoveryAnalytics?.failed_attempts ?? 0}
            </strong>

          </div>



          <div className="failure-item">

            <span>
              Successful Attempts
            </span>

            <strong>
              {recoveryAnalytics?.successful_attempts ?? 0}
            </strong>

          </div>



          <div className="failure-item">

            <span>
              Recovered Transactions
            </span>

            <strong>
              {recoveryAnalytics?.recovered_transactions ?? 0}
            </strong>

          </div>



          <div className="failure-item">

            <span>
              Failed Transactions
            </span>

            <strong>
              {recoveryAnalytics?.failed_transactions ?? 0}
            </strong>

          </div>



          <div className="failure-item">

            <span>
              Recovery Success Rate
            </span>

            <strong>

              {recoveryAnalytics
                ? `${recoveryAnalytics.recovery_success_rate_percent}%`

                : "0%"
              }

            </strong>

          </div>



          <div className="failure-item">

            <span>
              Average Attempts
            </span>

            <strong>
              {
                recoveryAnalytics
                  ?.average_attempts_per_recovery ?? 0
              }
            </strong>

          </div>


        </div>

      </section>



      {/* =====================================================
          GATEWAY PERFORMANCE
      ===================================================== */}

      <section className="card chart-card">

        <h2>
          Gateway Performance
        </h2>

        <p className="chart-description">

          Live gateway success rate based on transaction history

        </p>


        <ResponsiveContainer
          width="100%"
          height={300}
        >

          <BarChart
            data={gatewayChartData}
          >

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="gateway"
            />

            <YAxis
              domain={[0, 100]}
              tickFormatter={(value) =>
                `${value}%`
              }
            />

            <Tooltip
              formatter={(value) => [
                `${value}%`,
                "Success Rate"
              ]}
            />

            <Bar
              dataKey="successRate"
              name="Success Rate"
              radius={[8, 8, 0, 0]}
              fill="#7c5cff"
            />

          </BarChart>

        </ResponsiveContainer>

      </section>



      {/* =====================================================
          FAILURE DISTRIBUTION
      ===================================================== */}

      <section className="card chart-card">

        <h2>
          Failure Distribution
        </h2>

        <p className="chart-description">

          Distribution of payment failure reasons

        </p>


        <ResponsiveContainer
          width="100%"
          height={350}
        >

          <PieChart>

            <Pie
              data={failureChartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="45%"
              outerRadius={110}

              label={({
                name,
                percent
              }) =>
                `${name}: ${(percent * 100).toFixed(1)}%`
              }
            >

              {failureChartData.map(
                (entry, index) => (

                  <Cell
                    key={`cell-${index}`}
                    fill={
                      CHART_COLORS[
                        index %
                        CHART_COLORS.length
                      ]
                    }
                  />

                )
              )}

            </Pie>


            <Tooltip
              formatter={(value) => [
                value,
                "Failures"
              ]}
            />


            <Legend />

          </PieChart>

        </ResponsiveContainer>

      </section>



      {/* =====================================================
          RECOVERY PERFORMANCE
      ===================================================== */}

      <section className="card chart-card">

        <h2>
          Recovery Performance
        </h2>

        <p className="chart-description">

          Payment recovery attempt statistics

        </p>


        <ResponsiveContainer
          width="100%"
          height={300}
        >

          <BarChart
            data={recoveryChartData}
          >

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="name"
            />

            <YAxis />

            <Tooltip />

            <Bar
              dataKey="value"
              name="Transactions"
              radius={[8, 8, 0, 0]}
              fill="#00d4ff"
            />

          </BarChart>

        </ResponsiveContainer>

      </section>



      {/* =====================================================
          AI RECOVERY INTELLIGENCE
      ===================================================== */}

      <section className="card ai-card">

        {/* AI HEADER */}

        <div className="ai-title">

          <span className="ai-icon">
            🤖
          </span>

          <div>

            <h2>
              AI Recovery Intelligence
            </h2>

            <p>
              ML prediction + Recovery Agent + RAG + LLM
            </p>

          </div>

        </div>


        {/* EMPTY STATE */}

        {!result && !loading && (

          <div className="ai-placeholder">

            <div className="ai-empty-icon">
              🤖
            </div>

            <h3>
              Ready to Analyze
            </h3>

            <p>
              Process a payment to see the complete
              AI failure prediction and recovery decision.
            </p>

          </div>

        )}


        {/* LOADING STATE */}

        {loading && (

          <div className="ai-processing">

            <div className="loading-spinner">
              🤖
            </div>

            <h3>
              AI is analyzing the payment...
            </h3>

            <p>
              Running ML prediction, recovery policy,
              RAG retrieval and LLM explanation.
            </p>


            <div className="processing-steps">

              <div className="processing-step active">
                🧠 ML Prediction
              </div>

              <div className="processing-arrow">
                ↓
              </div>

              <div className="processing-step active">
                🤖 Recovery Agent
              </div>

              <div className="processing-arrow">
                ↓
              </div>

              <div className="processing-step active">
                📚 RAG Retrieval
              </div>

              <div className="processing-arrow">
                ↓
              </div>

              <div className="processing-step active">
                🦙 LLM Explanation
              </div>

            </div>

          </div>

        )}


        {/* RESULT */}

        {result && !loading && (

          <div className="ai-result">


            {/* =================================================
                TRANSACTION SUMMARY
            ================================================= */}

            <div className="ai-section-header">

              <span>
                💳
              </span>

              <h3>
                Transaction Analysis
              </h3>

            </div>


            <div className="ai-metrics-grid">


              {/* TRANSACTION ID */}

              <div className="ai-metric">

                <span>
                  Transaction ID
                </span>

                <strong>
                  {result.transaction_id}
                </strong>

              </div>


              {/* INITIAL STATUS */}

              <div className="ai-metric">

                <span>
                  Initial Payment
                </span>

                <strong
                  className={`status-badge ${
                    getStatusClass(
                      result.initial_payment?.status
                    )
                  }`}
                >

                  {formatStatus(
                    result.initial_payment?.status
                  )}

                </strong>

              </div>


              {/* FAILURE */}

              <div className="ai-metric">

                <span>
                  Failure Reason
                </span>

                <strong>
                  {
                    result.initial_payment?.failure_reason
                    || "NONE"
                  }
                </strong>

              </div>


              {/* ML PROBABILITY */}

              <div className="ai-metric">

                <span>
                  ML Failure Probability
                </span>

                <strong className="probability-value">

                  {
                    result.ml_prediction
                      ?.failure_probability_percent
                      ?? 0
                  }%

                </strong>

              </div>

            </div>



            {/* =================================================
                ML PREDICTION
            ================================================= */}

            <div className="ai-analysis-box">

              <div className="ai-analysis-title">

                <span>
                  🧠
                </span>

                <div>

                  <h3>
                    ML Failure Prediction
                  </h3>

                  <p>
                    Machine learning risk assessment
                  </p>

                </div>

              </div>


              <div className="probability-container">

                <div className="probability-header">

                  <span>
                    Failure Probability
                  </span>

                  <strong>

                    {
                      result.ml_prediction
                        ?.failure_probability_percent
                        ?? 0
                    }%

                  </strong>

                </div>


                <div className="probability-bar">

                  <div
                    className="probability-fill"
                    style={{
                      width: `${Math.min(
                        result.ml_prediction
                          ?.failure_probability_percent
                          ?? 0,
                        100
                      )}%`
                    }}
                  />

                </div>

              </div>

            </div>



            {/* =================================================
                RECOVERY AGENT
            ================================================= */}

            <div className="ai-analysis-box">

              <div className="ai-analysis-title">

                <span>
                  🤖
                </span>

                <div>

                  <h3>
                    Recovery Agent Decision
                  </h3>

                  <p>
                    Automated payment recovery strategy
                  </p>

                </div>

              </div>


              <div className="decision-grid">


                <div>

                  <span>
                    Action
                  </span>

                  <strong>

                    {
                      result.recovery
                        ?.recovery
                        ?.action
                      || "N/A"
                    }

                  </strong>

                </div>


                <div>

                  <span>
                    Decision
                  </span>

                  <strong>

                    {
                      result.recovery
                        ?.recovery
                        ?.decision
                      || "N/A"
                    }

                  </strong>

                </div>


                <div>

                  <span>
                    Recommended Gateway
                  </span>

                  <strong>

                    {
                      result.recovery
                        ?.recovery
                        ?.recommended_gateway
                      || "N/A"
                    }

                  </strong>

                </div>


                <div>

                  <span>
                    Final Gateway
                  </span>

                  <strong>

                    {
                      result.recovery
                        ?.final_gateway
                      || "N/A"
                    }

                  </strong>

                </div>


                <div>

                  <span>
                    Recovery Status
                  </span>

                  <strong
                    className={`status-badge ${
                      getStatusClass(
                        result.recovery?.status
                      )
                    }`}
                  >

                    {formatStatus(
                      result.recovery?.status
                    )}

                  </strong>

                </div>


                <div>

                  <span>
                    Decision Reason
                  </span>

                  <strong>

                    {
                      result.recovery
                        ?.recovery
                        ?.reason
                      || "N/A"
                    }

                  </strong>

                </div>


              </div>

            </div>



            {/* =================================================
                DECISION FLOW
            ================================================= */}

            <div className="ai-analysis-box">

              <div className="ai-analysis-title">

                <span>
                  🔄
                </span>

                <div>

                  <h3>
                    AI Decision Flow
                  </h3>

                  <p>
                    How the system handled this payment
                  </p>

                </div>

              </div>


              <div className="decision-flow">


                <div className="flow-step">

                  <div className="flow-icon">
                    💳
                  </div>

                  <strong>
                    Payment
                  </strong>

                  <small>
                    Transaction received
                  </small>

                </div>


                <div className="flow-arrow">
                  →
                </div>


                <div className="flow-step">

                  <div className="flow-icon">
                    🧠
                  </div>

                  <strong>
                    ML Prediction
                  </strong>

                  <small>
                    Failure risk calculated
                  </small>

                </div>


                <div className="flow-arrow">
                  →
                </div>


                <div className="flow-step">

                  <div className="flow-icon">
                    🤖
                  </div>

                  <strong>
                    Recovery Agent
                  </strong>

                  <small>
                    Recovery strategy selected
                  </small>

                </div>


                <div className="flow-arrow">
                  →
                </div>


                <div className="flow-step">

                  <div className="flow-icon">
                    📚
                  </div>

                  <strong>
                    RAG
                  </strong>

                  <small>
                    Policy retrieved
                  </small>

                </div>


                <div className="flow-arrow">
                  →
                </div>


                <div className="flow-step">

                  <div className="flow-icon">
                    🦙
                  </div>

                  <strong>
                    LLM
                  </strong>

                  <small>
                    Explanation generated
                  </small>

                </div>

              </div>

            </div>

            {/* ==========================================================
                RAG POLICY EVIDENCE
            ========================================================== */}

            {result?.rag_policy?.policies?.length > 0 && (

              <section className="card rag-card">

                <div className="ai-title">

                  <span className="ai-icon">
                    📚
                  </span>

                  <div>

                    <h2>
                      RAG Policy Evidence
                    </h2>

                    <p>
                      Retrieved recovery policies used by the AI
                    </p>

                  </div>

                </div>


                {/* Retrieval Summary */}

                <div className="rag-summary">

                  <div className="failure-item">

                    <span>
                      Policies Retrieved
                    </span>

                    <strong>
                      {result.rag_policy.documents_retrieved}
                    </strong>

                  </div>


                  <div className="failure-item">

                    <span>
                      Policy Source
                    </span>

                    <strong>
                      payment_recovery_policies.txt
                    </strong>

                  </div>

                </div>


                {/* Retrieved Policies */}

                <div className="rag-policies">

                  {result.rag_policy.policies.map(
                    (policy, index) => (

                      <div
                        className="rag-policy"
                        key={index}
                      >

                        <div className="rag-policy-header">

                          <h3>
                            Policy {index + 1}
                          </h3>

                          <span className="rag-score">

                            Similarity:{" "}

                            {(policy.score * 100).toFixed(2)}%

                          </span>

                        </div>


                        <p className="rag-document">

                          {policy.document}

                        </p>


                        <small>

                          Source: {policy.source}

                        </small>

                      </div>

                    )
                  )}

                </div>

              </section>

            )}

            {/* =================================================
                AI EXPLANATION
            ================================================= */}

            {result.ai_explanation && (

              <div className="ai-explanation">


                <div className="ai-explanation-header">

                  <span>
                    🦙
                  </span>

                  <div>

                    <h3>
                      AI Recovery Explanation
                    </h3>

                    <p>
                      Generated by the local Llama model
                    </p>

                  </div>

                </div>


                <div className="ai-explanation-content">

                  {result.ai_explanation}

                </div>


              </div>

            )}



            {/* =================================================
                PAYMENT ATTEMPTS
            ================================================= */}

            <div className="ai-analysis-box">

              <div className="ai-analysis-title">

                <span>
                  🔄
                </span>

                <div>

                  <h3>
                    Payment Recovery Attempts
                  </h3>

                  <p>
                    Gateway-by-gateway recovery history
                  </p>

                </div>

              </div>


              <div className="attempts-list">


                {result.recovery?.attempts?.length > 0 ? (

                  result.recovery.attempts.map(
                    (attempt, index) => (

                      <div
                        className="attempt-card"
                        key={index}
                      >


                        <div className="attempt-number">

                          {index + 1}

                        </div>


                        <div className="attempt-info">

                          <strong>

                            {attempt.gateway}

                          </strong>

                          <span>

                            Response Time:{" "}

                            {
                              attempt.response_time
                                ?? "N/A"
                            }

                            s

                          </span>

                        </div>


                        <div className="attempt-status">

                          <span
                            className={`status-badge ${
                              getStatusClass(
                                attempt.status
                              )
                            }`}
                          >

                            {formatStatus(
                              attempt.status
                            )}

                          </span>


                          {attempt.failure_reason && (

                            <small>

                              {attempt.failure_reason}

                            </small>

                          )}

                        </div>


                      </div>

                    )

                  )

                ) : (

                  <p>
                    No recovery attempts available.
                  </p>

                )}

              </div>

            </div>



            {/* =================================================
                FINAL RESULT
            ================================================= */}

            <div className="final-recovery-result">


              <div className="final-icon">

                {result.recovery?.status === "recovered"
                  ? "✅"
                  : "⚠️"
                }

              </div>


              <div>

                <h3>

                  {result.recovery?.status === "recovered"

                    ? "Payment Successfully Recovered"

                    : "Payment Recovery Not Completed"

                  }

                </h3>


                <p>

                  Final Gateway:{" "}

                  <strong>

                    {
                      result.recovery
                        ?.final_gateway
                      || "N/A"
                    }

                  </strong>

                </p>

              </div>

            </div>


          </div>

        )}

      </section>



      {/* =====================================================
          AI DECISION PIPELINE
      ===================================================== */}

      <section className="card">

        <h2>
          AI Decision Pipeline
        </h2>


        <div className="ai-placeholder">

          <p>

            💳 Payment Request

            {" → "}

            🧠 ML Failure Prediction

            {" → "}

            🤖 Recovery Agent

            {" → "}

            📚 RAG Policy Retrieval

            {" → "}

            🦙 LLM Explanation

            {" → "}

            🔄 Payment Recovery

          </p>

        </div>

      </section>



      {/* =====================================================
          TRANSACTION HISTORY
      ===================================================== */}

      <section className="card transaction-history">


        <h2>
          Transaction History
        </h2>


        <p className="description">

          Recent payment transactions and recovery outcomes

        </p>



        {transactions.length === 0 ? (

          <div className="ai-placeholder">

            <p>
              No transaction history available.
            </p>

          </div>

        ) : (

          <div className="transaction-table-wrapper">

            <table className="transaction-table">


              <thead>

                <tr>

                  <th>
                    Transaction ID
                  </th>

                  <th>
                    Amount
                  </th>

                  <th>
                    Method
                  </th>

                  <th>
                    Bank
                  </th>

                  <th>
                    Gateway
                  </th>

                  <th>
                    Status
                  </th>

                  <th>
                    Failure Reason
                  </th>

                </tr>

              </thead>



              <tbody>

                {transactions.map(
                  (transaction, index) => (

                    <tr
                      key={
                        `${transaction.transaction_id}-${index}`
                      }
                    >

                      <td>
                        {
                          transaction.transaction_id
                        }
                      </td>


                      <td>

                        {
                          transaction.amount !== null &&
                          transaction.amount !== undefined

                            ? `₹${Number(
                                transaction.amount
                              ).toLocaleString()}`

                            : "—"
                        }

                      </td>


                      <td>
                        {
                          transaction.payment_method ||
                          "—"
                        }
                      </td>


                      <td>
                        {
                          transaction.bank ||
                          "—"
                        }
                      </td>


                      <td>
                        {
                          transaction.gateway ||
                          "—"
                        }
                      </td>


                      <td>

                        <span
                          className={`status-badge ${
                            getStatusClass(
                              transaction.status
                            )
                          }`}
                        >

                          {formatStatus(
                            transaction.status
                          )}

                        </span>

                      </td>


                      <td>

                        {
                          transaction.failure_reason ||
                          "—"
                        }

                      </td>

                    </tr>

                  )
                )}

              </tbody>


            </table>

          </div>

        )}

      </section>


    </div>

  )

}


export default App