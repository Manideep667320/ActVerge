"""
build_benchmark_dataset.py
==========================
Generates the 100-scenario curated benchmark test set for ActVerge.
Covers 4 major real-world web domains with calibrated ground truth labels:
  - SUCCESS: 35
  - PARTIAL: 25
  - FAILED: 30
  - UNCERTAIN: 10
Total: 100 tasks.
"""

import json
from pathlib import Path

def generate_dataset() -> list[dict]:
    tasks = []

    # ══════════════════════════════════════════════════════════════════════════
    # 1. E-COMMERCE & RETAIL (30 tasks: 10 Success, 8 Partial, 9 Failed, 3 Uncertain)
    # ══════════════════════════════════════════════════════════════════════════

    # 1.1 SUCCESS (10)
    ecom_success = [
        ("ecom_001", "Add wireless noise-canceling headphones to cart on Amazon", "https://amazon.com/cart", "Amazon.com Shopping Cart",
         "<main><div class='cart-item'><h3>Sony WH-1000XM5 Wireless Headphones</h3><span class='price'>$348.00</span><span class='badge'>Added to Cart</span><span class='cart-count'>Cart: 1</span></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://amazon.com"}, {"step": 2, "action": "fill", "target": "input#twotabsearchtextbox", "value": "Sony WH-1000XM5"}, {"step": 3, "action": "click", "target": "input#add-to-cart-button"}],
         None),
        ("ecom_002", "Purchase 65-inch OLED 4K Smart TV on BestBuy", "https://bestbuy.com/checkout/confirm", "Order Confirmation - Best Buy",
         "<main class='order-confirmation'><h1>Thank You for Your Order!</h1><p class='order-id'>Order #BBY-98234-X</p><p class='item-title'>LG 65-inch Class C3 Series OLED 4K UHD Smart webOS TV</p><span class='status'>Status: Confirmed & Paid</span></main>",
         [{"step": 1, "action": "navigate", "target": "https://bestbuy.com"}, {"step": 2, "action": "click", "target": "button.checkout"}, {"step": 3, "action": "click", "target": "button.place-order"}],
         None),
        ("ecom_003", "Filter men's running shoes size 10 under $80 on Nike", "https://nike.com/w/mens-shoes-size-10", "Men's Running Shoes - Nike",
         "<main><div class='filter-chips'><span class='chip'>Size: 10</span><span class='chip'>Price: Under $80</span></div><div class='product-grid'><div class='product-card'><h4>Nike Revolution 7</h4><span class='price'>$65.00</span></div></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://nike.com"}, {"step": 2, "action": "click", "target": "input#filter-size-10"}, {"step": 3, "action": "click", "target": "input#filter-price-80"}],
         None),
        ("ecom_004", "Apply discount promo code SAVE20 on Shopify store checkout", "https://brandstore.com/checkout", "Checkout - BrandStore",
         "<div class='checkout-summary'><span class='promo-applied'>Promo code SAVE20 applied (-20%)</span><span class='discount-amount'>-$24.00</span><span class='total-price'>Total: $96.00</span></div>",
         [{"step": 1, "action": "fill", "target": "input#discount-code", "value": "SAVE20"}, {"step": 2, "action": "click", "target": "button#apply-discount"}],
         None),
        ("ecom_005", "Add mechanical gaming keyboard to wishlist on Newegg", "https://newegg.com/wishlist", "My Saved Wishlist - Newegg",
         "<main><div class='wishlist-container'><h2>Saved Items (1)</h2><div class='item'><span>Corsair K70 RGB Mechanical Keyboard</span><span class='tag'>Added to Wishlist</span></div></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://newegg.com"}, {"step": 2, "action": "click", "target": "button.add-to-wishlist"}],
         None),
        ("ecom_006", "Select 1-year product protection warranty plan on Walmart", "https://walmart.com/cart", "Walmart Shopping Cart",
         "<div class='cart-tray'><div class='cart-item'><span>Apple iPad 10th Gen</span><div class='addon-row'><span class='badge'>Allstate 2-Year Protection Plan Included</span><span class='addon-price'>+$44.00</span></div></div></div>",
         [{"step": 1, "action": "click", "target": "input#allstate-protection-plan"}],
         None),
        ("ecom_007", "Search organic fair-trade coffee beans on Target", "https://target.com/s?searchTerm=organic+coffee", "Organic Coffee : Target",
         "<main id='main-content'><h1>Results for 'organic fair-trade coffee beans' (42 items)</h1><div class='product-card'><span>Good & Gather Organic Whole Bean Coffee</span><span class='price'>$8.99</span></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://target.com"}, {"step": 2, "action": "fill", "target": "input#search", "value": "organic fair-trade coffee beans"}, {"step": 3, "action": "press_key", "value": "Enter"}],
         None),
        ("ecom_008", "Subscribe to monthly cat food delivery on Chewy", "https://chewy.com/autoship", "Manage Autoship - Chewy",
         "<main class='autoship-mgmt'><h2>Autoship Active</h2><p class='frequency'>Every 4 weeks</p><span class='item-name'>Purina ONE Tender Selects Cat Food (16 lb)</span><span class='status'>Next order ships in 28 days</span></main>",
         [{"step": 1, "action": "click", "target": "button#subscribe-autoship"}, {"step": 2, "action": "click", "target": "button#confirm-subscription"}],
         None),
        ("ecom_009", "Change shipping method to Express Overnight on eBay", "https://ebay.com/checkout", "eBay Checkout",
         "<div class='shipping-options'><label class='selected'><input type='radio' checked='' name='shipping'/><span class='title'>FedEx Express Overnight</span><span class='price'>$24.99</span><span class='delivery-date'>Delivery Tomorrow by 10:30 AM</span></label></div>",
         [{"step": 1, "action": "click", "target": "input[value='express-overnight']"}],
         None),
        ("ecom_010", "Redeem $50 electronic gift card balance on Sephora", "https://sephora.com/checkout/payment", "Payment Options - Sephora",
         "<div class='payment-methods'><div class='gift-card-applied'><span class='label'>Gift Card (Ending in 4092)</span><span class='balance-used'>-$50.00 Applied</span><span class='remaining-balance'>Order Balance Remaining: $12.50</span></div></div>",
         [{"step": 1, "action": "fill", "target": "input#gift-card-num", "value": "600492810492"}, {"step": 2, "action": "click", "target": "button#apply-gc"}],
         None),
    ]

    for tid, task, url, title, dom, trace, f_var in ecom_success:
        tasks.append({
            "task_id": tid, "domain": "E-Commerce", "user_task": task, "ground_truth": "SUCCESS", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 1.2 PARTIAL (8)
    ecom_partial = [
        ("ecom_011", "Search for ergonomic office chair under $200 on Amazon and display listings", "https://amazon.com", "Amazon.com. Spend less. Smile more.",
         "<main><input type='text' id='twotabsearchtextbox' name='q' value='ergonomic office chair under $200'/><button type='submit' id='nav-search-submit-button'>Go</button></main>",
         [{"step": 1, "action": "navigate", "target": "https://amazon.com"}, {"step": 2, "action": "fill", "target": "input#twotabsearchtextbox", "value": "ergonomic office chair under $200"}],
         "unsubmitted_search"),
        ("ecom_012", "Place order for electric toothbrush on Target with shipping address", "https://target.com/checkout", "Checkout : Target",
         "<form class='checkout-form'><input type='text' name='street' value='742 Evergreen Terrace'/><input type='text' name='city' value='Springfield'/><input type='text' name='zip' value='97477'/><button id='placeOrderBtn' type='button' class='btn-primary' disabled=''>Review Order</button></form>",
         [{"step": 1, "action": "fill", "target": "input[name='street']", "value": "742 Evergreen Terrace"}, {"step": 2, "action": "fill", "target": "input[name='city']", "value": "Springfield"}],
         "unsubmitted_checkout_draft"),
        ("ecom_013", "Select shoe size 11 and add to cart on Zappos", "https://zappos.com/product/109283", "Brooks Ghost 15 - Zappos",
         "<div class='product-options'><select id='size-select'><option value='11' selected=''>Size 11 (In Stock)</option></select><button id='addToCart' class='btn'>Add to Cart</button><span class='cart-status'>Cart: 0 items</span></div>",
         [{"step": 1, "action": "select", "target": "select#size-select", "value": "11"}],
         "unclicked_add_to_cart"),
        ("ecom_014", "Enter coupon discount code SAVE15 on ASOS checkout", "https://asos.com/bag", "Shopping Bag | ASOS",
         "<div class='promo-wrapper'><input type='text' id='promo-code-input' value='SAVE15'/><button id='apply-promo' type='button'>Apply Code</button><span class='discount-notice'>Code entered. Click Apply to validate.</span></div>",
         [{"step": 1, "action": "fill", "target": "input#promo-code-input", "value": "SAVE15"}],
         "unapplied_coupon_input"),
        ("ecom_015", "Set delivery address to work location on DoorDash", "https://doordash.com/address", "Delivery Address - DoorDash",
         "<div class='address-modal'><input type='text' id='address-input' value='500 5th Avenue, Suite 1200'/><input type='text' id='apt-input' value='Floor 12'/><button id='save-address-btn'>Save and Continue</button></div>",
         [{"step": 1, "action": "fill", "target": "input#address-input", "value": "500 5th Avenue, Suite 1200"}],
         "unsaved_address_modal"),
        ("ecom_016", "Configure custom gaming PC specifications on CyberPowerPC", "https://cyberpowerpc.com/configurator/pc", "Custom Gaming PC Configurator",
         "<div class='spec-builder'><div class='selected-specs'><span>CPU: Intel i7-14700K</span><span>RAM: 32GB DDR5</span></div><button id='save-config-btn' class='action-btn'>Save Configuration to Cart</button></div>",
         [{"step": 1, "action": "click", "target": "input#cpu-i7-14700k"}],
         "unfinalized_configuration"),
        ("ecom_017", "Fill customer return request form on Nordstrom", "https://nordstrom.com/returns", "Order Returns - Nordstrom",
         "<form id='return-form'><select name='reason'><option selected='' value='size_too_small'>Item too small</option></select><textarea name='notes'>Please exchange for size Medium.</textarea><button type='submit' id='submit-return'>Submit Return Request</button></form>",
         [{"step": 1, "action": "select", "target": "select[name='reason']", "value": "size_too_small"}],
         "unsubmitted_return_form"),
        ("ecom_018", "Select pickup in-store option for Apple MacBook on BestBuy", "https://bestbuy.com/cart", "Best Buy Cart",
         "<div class='fulfillment-selector'><label><input type='radio' name='fulfillment' checked='' value='store-pickup'/><span>Pick up in Store: Downtown Seattle (Ready in 1 hour)</span></label><button class='btn-checkout'>Proceed to Checkout</button></div>",
         [{"step": 1, "action": "click", "target": "input[value='store-pickup']"}],
         "checkout_uncommenced"),
    ]

    for tid, task, url, title, dom, trace, f_var in ecom_partial:
        tasks.append({
            "task_id": tid, "domain": "E-Commerce", "user_task": task, "ground_truth": "PARTIAL", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 1.3 FAILED (9)
    ecom_failed = [
        ("ecom_019", "Purchase mechanical gaming keyboard on Amazon", "https://github.com", "GitHub: Let’s build from here",
         "<main data-url='https://github.com'><h1>Where the world builds software</h1><p>Millions of developers and companies build, ship, and maintain software on GitHub.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://github.com"}],
         "agent_drift_domain_mismatch"),
        ("ecom_020", "Buy Nike Air Jordan 1 Retro sneakers on Nike Store", "https://nike.com/product/air-jordan-1-out-of-stock", "Product Not Available - Nike",
         "<main class='error-page'><div class='error-card'><h2>Sold Out / Out of Stock</h2><p>The requested product style is no longer available.</p><button class='btn-home'>Back to Homepage</button></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://nike.com/product/air-jordan-1"}],
         "out_of_stock_fatal_error"),
        ("ecom_021", "Order espresso machine on Target", "https://target.com/product/delonghi-404", "404 Page Not Found : Target",
         "<main><h1>We're sorry! The page you were looking for doesn't exist. (HTTP 404)</h1><a href='/'>Return to Target Home</a></main>",
         [{"step": 1, "action": "navigate", "target": "https://target.com/product/delonghi-404"}],
         "http_404_not_found"),
        ("ecom_022", "Pay credit card installment on Chase eCommerce checkout", "https://chase.com/payment-error", "Payment Declined - Chase",
         "<div class='error-banner alert-danger'><h3>Transaction Declined: Insufficient Funds (Error Code: 51)</h3><p>Please contact your financial institution or select an alternative payment method.</p></div>",
         [{"step": 1, "action": "click", "target": "button#submit-payment"}],
         "payment_declined_error"),
        ("ecom_023", "Search for 4K projector on B&H Photo Video", "https://bhphotovideo.com/search", "Search Results - B&H",
         "<main><div class='no-results'><h3>Zero results found for '4k projector xyz-99999-invalid'</h3><p>Check your spelling or try more general keywords.</p></div></main>",
         [{"step": 1, "action": "fill", "target": "input#search", "value": "4k projector xyz-99999-invalid"}, {"step": 2, "action": "press_key", "value": "Enter"}],
         "zero_search_results"),
        ("ecom_024", "Add ergonomic standing desk to cart on Wayfair", "https://wikipedia.org", "Wikipedia, the free encyclopedia",
         "<main id='content'><h1>Standing desk - Wikipedia</h1><p>A standing desk or stand-up desk is a desk conceived for writing or reading while standing up.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://wikipedia.org/wiki/Standing_desk"}],
         "hallucination_blog_drift"),
        ("ecom_025", "Reserve Apple iPhone 15 Pro at local Apple Store", "https://apple.com/shop/reserve/error", "Access Denied - Apple",
         "<main><h1>Access Denied (HTTP 403 Forbidden)</h1><p>You do not have permission to access this server or reservations are currently locked.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://apple.com/shop/reserve"}],
         "http_403_access_denied"),
        ("ecom_026", "Checkout vintage watch on Etsy", "https://etsy.com/cart/item-removed", "Cart Notice - Etsy",
         "<div class='notification-bar alert-warning'><span>Sorry, this one-of-a-kind item was purchased by another shopper while in your cart.</span></div>",
         [{"step": 1, "action": "click", "target": "button.checkout"}],
         "race_condition_item_removed"),
        ("ecom_027", "Apply store credit voucher on Overstock", "https://overstock.com/voucher/error", "Invalid Voucher - Overstock",
         "<div class='error-box'><h3>Error: Voucher EXPIRED_OR_INVALID</h3><p>The code entered has already been redeemed or is expired.</p></div>",
         [{"step": 1, "action": "fill", "target": "input#voucher", "value": "CREDIT50EXPIRED"}, {"step": 2, "action": "click", "target": "button#apply"}],
         "expired_voucher_error"),
    ]

    for tid, task, url, title, dom, trace, f_var in ecom_failed:
        tasks.append({
            "task_id": tid, "domain": "E-Commerce", "user_task": task, "ground_truth": "FAILED", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": ["Error: Action failed"], "network_logs": [{"status": 400, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 1.4 UNCERTAIN (3)
    ecom_uncertain = [
        ("ecom_028", "Finalize payment for luxury watch on Chrono24", "https://chrono24.com/checkout/processing", "Processing Order...",
         "<div class='loading-spinner-overlay'><div class='spinner'></div><p>Contacting merchant gateway... Please do not refresh this page.</p></div>",
         [{"step": 1, "action": "click", "target": "button#pay-now"}],
         "infinite_loading_spinner"),
        ("ecom_029", "View 3D product model preview for sofa on IKEA", "https://ikea.com/product/sofa-3d", "IKEA 3D Viewer",
         "<main><canvas id='webgl-3d-canvas' width='1280' height='800'></canvas><div class='canvas-controls'><span>Rotate: Drag | Zoom: Pinch</span></div></main>",
         [{"step": 1, "action": "click", "target": "button#launch-3d"}],
         "opaque_webgl_canvas_rendering"),
        ("ecom_030", "Verify flash deal countdown timer on AliExpress", "https://aliexpress.com/deals", "AliExpress Flash Deals",
         "<div class='deals-wrapper'><div class='skeleton-placeholder'></div><div class='skeleton-card'></div></div>",
         [{"step": 1, "action": "navigate", "target": "https://aliexpress.com/deals"}],
         "skeleton_screen_hydration_lag"),
    ]

    for tid, task, url, title, dom, trace, f_var in ecom_uncertain:
        tasks.append({
            "task_id": tid, "domain": "E-Commerce", "user_task": task, "ground_truth": "UNCERTAIN", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })


    # ══════════════════════════════════════════════════════════════════════════
    # 2. PRODUCTIVITY & FORMS (25 tasks: 9 Success, 7 Partial, 7 Failed, 2 Uncertain)
    # ══════════════════════════════════════════════════════════════════════════

    # 2.1 SUCCESS (9)
    prod_success = [
        ("prod_001", "Create simple Google Form with customer satisfaction question", "https://docs.google.com/forms/d/1aB9x/edit", "Customer Feedback Form - Google Forms",
         "<div class='form-editor-canvas'><h2>Customer Feedback Survey</h2><div class='question-card' data-type='multiple_choice'><h3>How satisfied were you with our service?</h3><div class='option'>1 - Very Unsatisfied</div><div class='option'>2 - Neutral</div><div class='option'>3 - Very Satisfied</div></div></div>",
         [{"step": 1, "action": "navigate", "target": "https://forms.new"}, {"step": 2, "action": "fill", "target": "div[aria-label='Form title']", "value": "Customer Feedback Survey"}, {"step": 3, "action": "fill", "target": "textarea.question-title", "value": "How satisfied were you with our service?"}],
         None),
        ("prod_002", "Draft quarterly product update summary document in Google Docs", "https://docs.google.com/document/d/99zQ/edit", "Q3 Product Update - Google Docs",
         "<div class='kix-appview-editor'><div class='kix-page-content'><h1 class='doc-title'>Q3 Product Roadmap & Milestone Summary</h1><p>In Q3, the engineering team shipped 42 features, reduced API response latency by 35%, and onboarded 12 enterprise clients.</p></div></div>",
         [{"step": 1, "action": "navigate", "target": "https://docs.new"}, {"step": 2, "action": "fill", "target": "div.kix-page", "value": "Q3 Product Roadmap & Milestone Summary\nIn Q3..."}],
         None),
        ("prod_003", "Create high-priority bug ticket for login failure in Jira", "https://company.atlassian.net/browse/SEC-104", "[SEC-104] Authentication 2FA SMS code timeout - Jira",
         "<div class='issue-view'><h1 id='summary-val'>[SEC-104] Authentication 2FA SMS code timeout</h1><div class='issue-details'><span class='priority-high'>High Priority</span><span class='status-badge'>Status: Open</span><div class='desc'>SMS verification codes expire before delivery on T-Mobile.</div></div></div>",
         [{"step": 1, "action": "click", "target": "button#create-issue"}, {"step": 2, "action": "fill", "target": "input#summary", "value": "[SEC-104] Authentication 2FA SMS code timeout"}, {"step": 3, "action": "click", "target": "button#create-submit"}],
         None),
        ("prod_004", "Build 3-question event registration survey in Typeform", "https://admin.typeform.com/form/t8923/edit", "Tech Summit 2026 Registration - Typeform",
         "<div class='typeform-canvas'><div class='step-card'><span>1. What is your full legal name?</span></div><div class='step-card'><span>2. What is your organization or company?</span></div><div class='step-card'><span>3. Do you require dietary accommodations?</span></div></div>",
         [{"step": 1, "action": "click", "target": "button.add-question"}],
         None),
        ("prod_005", "Submit travel expense reimbursement form in Workday", "https://myworkday.com/expense/confirm", "Expense Report Submitted - Workday",
         "<main class='confirmation-container'><h1>Expense Report EXP-88912 Submitted</h1><span class='status'>Approval Status: Pending Manager Review</span><p class='amount'>Total Amount: $450.00 USD</p></main>",
         [{"step": 1, "action": "fill", "target": "input#expense-amount", "value": "450.00"}, {"step": 2, "action": "click", "target": "button#submit-expense"}],
         None),
        ("prod_006", "Create new meeting notes page titled Weekly Sprint Retro in Notion", "https://notion.so/workspace/weekly-sprint-retro-102", "Weekly Sprint Retro - Notion",
         "<div class='notion-page-content'><h1 class='notion-title'>Weekly Sprint Retro</h1><div class='notion-block'><h3>What went well?</h3><p>Fast sprint delivery, all blockers cleared early.</p></div><div class='notion-block'><h3>What needs improvement?</h3><p>Earlier design reviews for complex UX.</p></div></div>",
         [{"step": 1, "action": "fill", "target": "div[placeholder='Untitled']", "value": "Weekly Sprint Retro"}],
         None),
        ("prod_007", "Send meeting invitation email in Google Workspace Gmail", "https://mail.google.com/mail/u/0/#sent", "Sent Mail - Gmail",
         "<div class='sent-notification-bar'><span>Message sent.</span><a href='#'>View message</a></div><div class='mail-list-item'><span class='recipient'>engineering-team@company.com</span><span class='subject'>Architecture Review Sync Tomorrow @ 2 PM</span></div>",
         [{"step": 1, "action": "click", "target": "button.compose"}, {"step": 2, "action": "click", "target": "div.send-btn"}],
         None),
        ("prod_008", "Add new employee record to BambooHR directory", "https://company.bamboohr.com/employees/profile/992", "Jane Doe - BambooHR Profile",
         "<div class='profile-header'><h1>Jane Doe</h1><span class='job-title'>Senior Software Engineer</span><span class='dept'>Cloud Platforms</span><span class='status-active'>Status: Active Employee</span></div>",
         [{"step": 1, "action": "click", "target": "button#save-employee"}],
         None),
        ("prod_009", "Export weekly sales spreadsheet to CSV on Airtable", "https://airtable.com/app1234/tblSales", "Sales Pipeline - Airtable",
         "<div class='toast-notification alert-success'><span>CSV export complete: Sales_Pipeline_Q3_2026.csv downloaded.</span></div>",
         [{"step": 1, "action": "click", "target": "button.view-menu"}, {"step": 2, "action": "click", "target": "button.download-csv"}],
         None),
    ]

    for tid, task, url, title, dom, trace, f_var in prod_success:
        tasks.append({
            "task_id": tid, "domain": "Productivity", "user_task": task, "ground_truth": "SUCCESS", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "creator" if "Create" in task or "Draft" in task or "Build" in task else "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 2.2 PARTIAL (7)
    prod_partial = [
        ("prod_010", "Tell Gemini in Google Forms to prepare a 3-question student survey", "https://docs.google.com/forms/d/1xYz/edit", "Untitled form - Google Forms",
         "<div class='gemini-ai-sidebar'><textarea id='gemini-prompt-input' value='Prepare a 3-question survey about student homework habits and study hours'/><button class='btn-create-prompt'>Generate Questions</button></div><div class='form-canvas'><h2 class='empty-title'>Untitled form</h2><p class='no-questions-placeholder'>No questions added yet. Insert from Gemini sidebar or click + to add.</p></div>",
         [{"step": 1, "action": "navigate", "target": "https://forms.new"}, {"step": 2, "action": "fill", "target": "textarea#gemini-prompt-input", "value": "Prepare a 3-question survey about student homework habits"}],
         "ai_prompt_typed_canvas_empty"),
        ("prod_011", "Fill out and submit employee feedback form on Google Forms", "https://docs.google.com/forms/d/e/1FAIpQLSc/viewform", "Annual Employee Engagement Survey",
         "<form id='mG61Hd'><input type='text' name='entry.1029' value='Everything is great with my team'/><input type='radio' name='entry.4820' checked='' value='5'/><button type='submit' class='submit-btn'>Submit</button></form><div class='unsubmitted-notice'>Response has not been submitted yet.</div>",
         [{"step": 1, "action": "fill", "target": "input[name='entry.1029']", "value": "Everything is great with my team"}],
         "unsubmitted_form_response"),
        ("prod_012", "Draft customer outreach email in Gmail compose window", "https://mail.google.com/mail/u/0/#inbox", "Inbox (12) - Gmail",
         "<div class='compose-window'><input name='to' value='client@enterprise.com'/><input name='subject' value='ActVerge Enterprise Partnership Proposal'/><div class='editable-body'>Dear John,\nI am writing to share our latest benchmark results...</div><button class='send-button'>Send</button></div>",
         [{"step": 1, "action": "click", "target": "button.compose"}, {"step": 2, "action": "fill", "target": "input[name='to']", "value": "client@enterprise.com"}],
         "unsent_draft_email"),
        ("prod_013", "Fill Jira issue creation form for UI responsiveness bug", "https://company.atlassian.net/jira/your-work", "Create Issue - Jira",
         "<div class='modal-dialog'><input id='summary' value='Mobile navigation hamburger menu overlaps logo'/><textarea id='description'>Observed on iPhone 15 Pro viewport...</textarea><button id='create-issue-submit' class='btn-primary'>Create</button></div>",
         [{"step": 1, "action": "fill", "target": "input#summary", "value": "Mobile navigation hamburger menu overlaps logo"}],
         "unclicked_modal_submission"),
        ("prod_014", "Enter student grades spreadsheet data in Google Sheets", "https://docs.google.com/spreadsheets/d/4829/edit", "CS101 Final Grades - Google Sheets",
         "<div class='waffle-cell-editor'><input id='cell-input' value='94.5'/><span class='cell-location'>Cell C12</span></div><div class='save-status'>Saving changes in memory... Press Enter to commit.</div>",
         [{"step": 1, "action": "fill", "target": "input#cell-input", "value": "94.5"}],
         "uncommitted_sheet_cell_edit"),
        ("prod_015", "Prepare presentation outline in Google Slides", "https://docs.google.com/presentation/d/9021/edit", "Untitled presentation - Google Slides",
         "<div class='slide-canvas'><div class='title-box'><input value='ActVerge: Autonomous Agent Verification Framework'/></div><div class='subtitle-box'>Click to add subtitle</div></div>",
         [{"step": 1, "action": "fill", "target": "div.title-box input", "value": "ActVerge: Autonomous Agent Verification Framework"}],
         "unpopulated_body_canvas"),
        ("prod_016", "Configure team access permissions on Slack channel settings", "https://app.slack.com/client/T123/C456", "Channel Settings - Slack",
         "<div class='slack-modal'><label><input type='checkbox' checked='' id='private-toggle'/><span>Make channel private</span></label><button id='save-settings-btn' class='btn'>Save Changes</button></div>",
         [{"step": 1, "action": "click", "target": "input#private-toggle"}],
         "unconfirmed_settings_save"),
    ]

    for tid, task, url, title, dom, trace, f_var in prod_partial:
        tasks.append({
            "task_id": tid, "domain": "Productivity", "user_task": task, "ground_truth": "PARTIAL", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "creator" if "Gemini" in task or "outline" in task else "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 2.3 FAILED (7)
    prod_failed = [
        ("prod_017", "Prepare simple Google Form for team lunch order", "https://github.com", "GitHub: Let’s build from here",
         "<main><title>GitHub</title><h1>Where software is built</h1><p>GitHub is the home for developer tools.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://github.com"}],
         "agent_drift_domain_mismatch"),
        ("prod_018", "Submit customer contract on DocuSign", "https://docusign.net/error/session-timeout", "Session Expired - DocuSign",
         "<div class='error-envelope'><h2>Session Timed Out (Security Error)</h2><p>Your authentication token has expired. Please re-authenticate to sign document.</p></div>",
         [{"step": 1, "action": "navigate", "target": "https://docusign.net"}],
         "session_timeout_fatal"),
        ("prod_019", "Create Google Sheet for company annual budget", "https://docs.google.com/spreadsheets/u/0/quota-exceeded", "Google Drive - Storage Full",
         "<main><h2>Drive Storage Limit Reached</h2><p>You cannot create or upload new files until you free up space or upgrade storage quota.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://sheets.new"}],
         "storage_quota_exceeded"),
        ("prod_020", "Export quarterly performance report on Salesforce", "https://salesforce.com/lightning/error/403", "Insufficient Privileges - Salesforce",
         "<div class='alert-error'><h1>Insufficient Privileges</h1><p>You do not have the necessary profile permissions to export reports in this organization.</p></div>",
         [{"step": 1, "action": "click", "target": "button#export-report"}],
         "rbac_permission_denied"),
        ("prod_021", "Schedule all-hands meeting on Microsoft Outlook Calendar", "https://outlook.office.com/calendar/conflict", "Room Conflict - Outlook",
         "<div class='conflict-banner'><h3>Scheduling Conflict Detected</h3><p>Selected room 'Grand Boardroom' is already reserved by Executive Team at this time.</p></div>",
         [{"step": 1, "action": "click", "target": "button#send-invite"}],
         "resource_reservation_conflict"),
        ("prod_022", "Update customer address record in HubSpot CRM", "https://wikipedia.org", "Customer relationship management - Wikipedia",
         "<main><h1>Customer relationship management</h1><p>Customer relationship management (CRM) is a process in which a business administers interactions with customers.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://wikipedia.org/wiki/Customer_relationship_management"}],
         "hallucination_informational_drift"),
        ("prod_023", "Submit anonymous company feedback survey on SurveyMonkey", "https://surveymonkey.com/r/closed", "Survey Closed - SurveyMonkey",
         "<main class='closed-container'><h2>This survey is now closed.</h2><p>The survey creator is no longer accepting new responses.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://surveymonkey.com/r/company-survey"}],
         "survey_closed_error"),
    ]

    for tid, task, url, title, dom, trace, f_var in prod_failed:
        tasks.append({
            "task_id": tid, "domain": "Productivity", "user_task": task, "ground_truth": "FAILED", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": ["Error: Task terminated with fatal error"], "network_logs": [{"status": 403, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 2.4 UNCERTAIN (2)
    prod_uncertain = [
        ("prod_024", "Generate AI project timeline chart on Miro whiteboard", "https://miro.com/app/board/uX892", "Project Roadmap - Miro",
         "<div class='miro-board-wrapper'><canvas id='board-canvas' width='1920' height='1080'></canvas><div class='status-overlay'>Syncing live collaborator updates...</div></div>",
         [{"step": 1, "action": "click", "target": "button.generate-ai-timeline"}],
         "uninspectable_canvas_board"),
        ("prod_025", "Execute database schema migration on Supabase Studio", "https://supabase.com/dashboard/project/db/migrate", "Running Migrations...",
         "<div class='migration-progress'><h3>Applying migration 20261031_init.sql</h3><div class='indeterminate-progress-bar'></div><p>Executing DDL statements... Please wait.</p></div>",
         [{"step": 1, "action": "click", "target": "button.run-migration"}],
         "asynchronous_ddl_pending"),
    ]

    for tid, task, url, title, dom, trace, f_var in prod_uncertain:
        tasks.append({
            "task_id": tid, "domain": "Productivity", "user_task": task, "ground_truth": "UNCERTAIN", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })


    # ══════════════════════════════════════════════════════════════════════════
    # 3. DEVELOPER PLATFORMS & CLOUD (25 tasks: 9 Success, 5 Partial, 8 Failed, 3 Uncertain)
    # ══════════════════════════════════════════════════════════════════════════

    # 3.1 SUCCESS (9)
    dev_success = [
        ("dev_001", "Find Playwright Python installation command on official documentation", "https://playwright.dev/python/docs/intro", "Installation | Playwright Python",
         "<main class='doc-content'><h1>Installation</h1><p>Get started by installing Playwright with pip:</p><pre><code>pip install pytest-playwright\nplaywright install</code></pre></main>",
         [{"step": 1, "action": "navigate", "target": "https://playwright.dev/python"}, {"step": 2, "action": "click", "target": "a[href='/python/docs/intro']"}],
         None),
        ("dev_002", "Inspect latest commit on main branch for ActVerge repository", "https://github.com/Manideep667320/ActVerge", "GitHub - Manideep667320/ActVerge",
         "<main><div class='repo-header'><h1>Manideep667320 / ActVerge</h1></div><div class='commit-tease'><span class='commit-title'>fix(backend): use NullPool and engine disposal in tests</span><span class='commit-sha'>3a26948</span><span class='branch-name'>Branch: main</span></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://github.com/Manideep667320/ActVerge"}],
         None),
        ("dev_003", "Search official Redis Docker image tags on Docker Hub", "https://hub.docker.com/_/redis/tags", "redis - Docker Hub Tags",
         "<div class='tag-list'><div class='tag-row'><h3>redis:7.4-alpine</h3><span class='badge'>Official Image</span><span class='digest'>sha256:88942b10</span></div><div class='tag-row'><h3>redis:7.2-bookworm</h3><span class='badge'>Official Image</span></div></div>",
         [{"step": 1, "action": "navigate", "target": "https://hub.docker.com/_/redis/tags"}],
         None),
        ("dev_004", "Create GitHub pull request titled Add Multi-Modal Verifier", "https://github.com/organization/repo/pull/42", "Add Multi-Modal Verifier by agent · Pull Request #42",
         "<div class='pr-view'><h1 class='pr-title'>Add Multi-Modal Verifier <span class='pr-number'>#42</span></h1><span class='pr-state-open'>Open</span><p>Merge 4 commits into <code>main</code> from <code>feature/verifier</code></p></div>",
         [{"step": 1, "action": "click", "target": "button#create-pull-request"}],
         None),
        ("dev_005", "Star the langchain-ai/langgraph repository on GitHub", "https://github.com/langchain-ai/langgraph", "GitHub - langchain-ai/langgraph",
         "<div class='repo-actions'><button class='btn-starred' aria-label='Unstar this repository'><span class='starred-label'>Starred</span><span class='count'>14.8k</span></button></div>",
         [{"step": 1, "action": "click", "target": "button.starred"}],
         None),
        ("dev_006", "Search for FastAPI CORS middleware example on StackOverflow", "https://stackoverflow.com/questions/65634702", "How to enable CORS in FastAPI? - Stack Overflow",
         "<main id='mainbar'><h1>How to enable CORS in FastAPI?</h1><div class='accepted-answer'><span class='accepted-badge'>Accepted Answer (Score: 245)</span><pre><code>from fastapi.middleware.cors import CORSMiddleware\napp.add_middleware(CORSMiddleware, allow_origins=['*'])</code></pre></div></main>",
         [{"step": 1, "action": "fill", "target": "input[name='q']", "value": "FastAPI CORS middleware example"}, {"step": 2, "action": "press_key", "value": "Enter"}],
         None),
        ("dev_007", "Generate personal access token on GitHub developer settings", "https://github.com/settings/tokens", "Personal Access Tokens - GitHub",
         "<div class='token-created-banner alert-success'><h3>Token successfully generated!</h3><p>Make sure to copy your personal access token now. You won't be able to see it again.</p><code>ghp_984128941941914921491429</code></div>",
         [{"step": 1, "action": "click", "target": "button#generate-token"}],
         None),
        ("dev_008", "Verify AWS S3 bucket creation in AWS Management Console", "https://s3.console.aws.amazon.com/s3/buckets/actverge-artifacts", "Amazon S3 - Buckets - actverge-artifacts",
         "<main><div class='bucket-overview'><h1>actverge-artifacts</h1><span class='region'>Region: us-east-1</span><span class='access'>Access: Bucket and objects not public</span><span class='status'>Status: Active</span></div></main>",
         [{"step": 1, "action": "click", "target": "button#create-bucket"}],
         None),
        ("dev_009", "Find latest released version of Pydantic on PyPI", "https://pypi.org/project/pydantic", "pydantic · PyPI",
         "<main><div class='package-header'><h1>pydantic 2.9.2</h1><p class='summary'>Data validation using Python type hints.</p><span class='pip-command'>pip install pydantic</span></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://pypi.org/project/pydantic"}],
         None),
    ]

    for tid, task, url, title, dom, trace, f_var in dev_success:
        tasks.append({
            "task_id": tid, "domain": "Developer Tools", "user_task": task, "ground_truth": "SUCCESS", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 3.2 PARTIAL (5)
    dev_partial = [
        ("dev_010", "Search for high-performance python async database drivers on GitHub", "https://github.com", "GitHub: Let’s build from here",
         "<header><input type='text' name='q' value='high-performance python async database drivers'/><div class='search-suggestions'><span>Search across all of GitHub</span></div></header>",
         [{"step": 1, "action": "fill", "target": "input[name='q']", "value": "high-performance python async database drivers"}],
         "unsubmitted_search_query"),
        ("dev_011", "Open new issue on repository reporting memory leak", "https://github.com/organization/repo/issues/new", "New Issue · organization/repo",
         "<form class='issue-form'><input id='issue_title' value='Memory leak in connection pool during concurrent stress'/><textarea id='issue_body'>Steps to reproduce:\n1. Run load test with 500 workers...</textarea><button type='submit' class='btn-primary'>Submit new issue</button></form>",
         [{"step": 1, "action": "fill", "target": "input#issue_title", "value": "Memory leak in connection pool"}],
         "unsubmitted_issue_draft"),
        ("dev_012", "Configure webhook endpoint URL in Stripe developer dashboard", "https://dashboard.stripe.com/test/webhooks/create", "Add a webhook endpoint - Stripe",
         "<div class='webhook-modal'><input id='endpoint-url' value='https://api.actverge.dev/webhooks/stripe'/><div class='events-selected'><span>2 events selected: payment_intent.succeeded, charge.refunded</span></div><button id='save-webhook'>Add endpoint</button></div>",
         [{"step": 1, "action": "fill", "target": "input#endpoint-url", "value": "https://api.actverge.dev/webhooks/stripe"}],
         "unconfirmed_webhook_save"),
        ("dev_013", "Fork repository to personal account on GitLab", "https://gitlab.com/project/group/forks/new", "Fork project · GitLab",
         "<div class='fork-destination'><select id='namespace'><option value='user-manideep' selected=''>Manideep Masna (@user-manideep)</option></select><button id='confirm-fork-btn'>Fork project</button></div>",
         [{"step": 1, "action": "select", "target": "select#namespace", "value": "user-manideep"}],
         "untriggered_fork_action"),
        ("dev_014", "Select environment variables file in Vercel project deployment", "https://vercel.com/dashboard/project/settings/environment-variables", "Environment Variables - Vercel",
         "<div class='env-form'><input placeholder='KEY' value='DATABASE_URL'/><input placeholder='VALUE' value='postgresql+asyncpg://...'/><button class='btn-add'>Save</button></div>",
         [{"step": 1, "action": "fill", "target": "input[placeholder='KEY']", "value": "DATABASE_URL"}],
         "uncommitted_env_variable"),
    ]

    for tid, task, url, title, dom, trace, f_var in dev_partial:
        tasks.append({
            "task_id": tid, "domain": "Developer Tools", "user_task": task, "ground_truth": "PARTIAL", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 3.3 FAILED (8)
    dev_failed = [
        ("dev_015", "Search for Python AsyncIO tutorials on GitHub", "https://kayak.com/flights", "Search Flights - KAYAK",
         "<main><h1>Find cheap flight tickets from New York to London</h1><span class='fare'>$480 roundtrip</span></main>",
         [{"step": 1, "action": "navigate", "target": "https://kayak.com"}],
         "agent_drift_domain_mismatch"),
        ("dev_016", "View internal documentation repository on GitHub", "https://github.com/company/internal-secret-repo", "Page not found · GitHub · GitHub",
         "<main id='content'><h1>404</h1><p>This is not the web page you are looking for.</p><a href='/'>Find your way home</a></main>",
         [{"step": 1, "action": "navigate", "target": "https://github.com/company/internal-secret-repo"}],
         "http_404_not_found"),
        ("dev_017", "Deploy Docker container to Kubernetes cluster on GKE", "https://console.cloud.google.com/kubernetes/deploy/error", "Kubernetes Error - Cloud Console",
         "<div class='alert-card alert-error'><h3>Deployment Failed: CrashLoopBackOff</h3><p>Back-off 5m0s restarting failed container: OOMKilled (Exit Code 137).</p></div>",
         [{"step": 1, "action": "click", "target": "button.deploy"}],
         "kubernetes_crash_loop_backoff"),
        ("dev_018", "Query GitHub REST API for repository contributors", "https://api.github.com/rate_limit", "API Rate Limit Exceeded",
         "<pre>{'message': 'API rate limit exceeded for client IP. Maximum 60 requests per hour allowed for unauthenticated access.'}</pre>",
         [{"step": 1, "action": "navigate", "target": "https://api.github.com/repos/org/repo/contributors"}],
         "rate_limit_exceeded_error"),
        ("dev_019", "Clone private repository using SSH key on Bitbucket", "https://bitbucket.org/account/ssh/denied", "Access Denied - Bitbucket",
         "<div class='error-box'><h2>Permission denied (publickey).</h2><p>Could not read from remote repository. Verify SSH public key credentials.</p></div>",
         [{"step": 1, "action": "click", "target": "button#clone-repo"}],
         "ssh_key_permission_denied"),
        ("dev_020", "Publish npm package to public registry", "https://npmjs.com/package/publish/error", "Publish Error - npm",
         "<div class='error-log'><code>npm error code E403\nnpm error 403 Forbidden - PUT https://registry.npmjs.org/pkg - You cannot publish over the previously published versions: 1.0.0.</code></div>",
         [{"step": 1, "action": "click", "target": "button#publish"}],
         "npm_version_conflict_403"),
        ("dev_021", "Connect MongoDB Atlas cluster via Cloud connection string", "https://cloud.mongodb.com/cluster/whitelist-error", "IP Whitelist Error - MongoDB Atlas",
         "<div class='alert-box'><h3>Connection refused: IP Address Not Whitelisted</h3><p>Your current client IP (192.0.2.1) is not authorized in Network Access security rules.</p></div>",
         [{"step": 1, "action": "click", "target": "button#test-connection"}],
         "ip_whitelist_security_block"),
        ("dev_022", "Inspect Travis CI automated build logs for Pull Request", "https://travis-ci.com/org/repo/builds/992", "Build #992 Errored - Travis CI",
         "<div class='build-status status-errored'><h1>Build #992 Errored</h1><span class='exit-code'>Command terminated with exit code 2 (SyntaxError in migration.py).</span></div>",
         [{"step": 1, "action": "navigate", "target": "https://travis-ci.com/org/repo/builds/992"}],
         "ci_build_fatal_error"),
    ]

    for tid, task, url, title, dom, trace, f_var in dev_failed:
        tasks.append({
            "task_id": tid, "domain": "Developer Tools", "user_task": task, "ground_truth": "FAILED", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": ["Fatal build/execution error"], "network_logs": [{"status": 404, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 3.4 UNCERTAIN (3)
    dev_uncertain = [
        ("dev_023", "Inspect interactive Grafana system metrics dashboard", "https://grafana.internal/d/system-metrics", "Grafana - System Metrics",
         "<div class='grafana-dashboard'><canvas class='u-over' width='800' height='300'></canvas><span class='refresh-badge'>Auto-refresh: 5s</span></div>",
         [{"step": 1, "action": "navigate", "target": "https://grafana.internal/d/system-metrics"}],
         "unparsed_html5_canvas_telemetry"),
        ("dev_024", "Authenticate Single Sign-On via Okta IdP redirect", "https://auth.company.okta.com/oauth2/v1/authorize", "Authenticating...",
         "<div class='auth-redirect'><p>Waiting for SAML 2.0 assertions... Browser will redirect automatically.</p></div>",
         [{"step": 1, "action": "click", "target": "button#sso-login"}],
         "intermediate_oauth_redirect"),
        ("dev_025", "Trigger automated database backup snapshot on CockroachDB Cloud", "https://cockroachlabs.cloud/cluster/backup/status", "Backup Job Status",
         "<div class='job-container'><h3>Snapshot Job #BK-4921 in progress</h3><span class='progress-label'>38% completed (24.1 GB transferred)</span></div>",
         [{"step": 1, "action": "click", "target": "button#create-snapshot"}],
         "long_running_async_job"),
    ]

    for tid, task, url, title, dom, trace, f_var in dev_uncertain:
        tasks.append({
            "task_id": tid, "domain": "Developer Tools", "user_task": task, "ground_truth": "UNCERTAIN", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })


    # ══════════════════════════════════════════════════════════════════════════
    # 4. TRAVEL, BOOKING & SEARCH (20 tasks: 7 Success, 5 Partial, 6 Failed, 2 Uncertain)
    # ══════════════════════════════════════════════════════════════════════════

    # 4.1 SUCCESS (7)
    travel_success = [
        ("travel_001", "Search non-stop flights from New York to London under $500 on Kayak", "https://kayak.com/flights/NYC-LON", "Cheap Flights, New York to London - KAYAK",
         "<main class='flight-results'><h1>NYC to LON Flights</h1><div class='flight-card'><span class='airline'>Virgin Atlantic (Non-stop)</span><span class='price'>$480 roundtrip</span><span class='status'>Available for Booking</span></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://kayak.com/flights"}, {"step": 2, "action": "fill", "target": "input[placeholder='From?']", "value": "New York (NYC)"}, {"step": 3, "action": "click", "target": "button[aria-label='Search flights']"}],
         None),
        ("travel_002", "Reserve queen room at Hilton Downtown for 3 nights on Booking.com", "https://booking.com/confirmation/hilton-queen", "Booking Confirmation - Booking.com",
         "<main class='reservation-confirmed'><h1>Your reservation is confirmed!</h1><p class='res-id'>Confirmation Number: 4920.194.021</p><p class='hotel-title'>Hilton Garden Inn Seattle Downtown</p><span class='dates'>Check-in: Nov 12 - Check-out: Nov 15</span></main>",
         [{"step": 1, "action": "click", "target": "button#confirm-reservation"}],
         None),
        ("travel_003", "Check today's local weather forecast and temperature in Tokyo", "https://weather.com/weather/today/l/Tokyo", "Tokyo, Japan Weather Forecast - The Weather Channel",
         "<div class='today-weather'><h1>Tokyo, Tokyo, Japan Weather</h1><span class='current-temp'>68°F</span><p class='conditions'>Sunny & Clear</p><span class='humidity'>Humidity: 48%</span></div>",
         [{"step": 1, "action": "navigate", "target": "https://weather.com"}, {"step": 2, "action": "fill", "target": "input#LocationSearch", "value": "Tokyo"}, {"step": 3, "action": "press_key", "value": "Enter"}],
         None),
        ("travel_004", "Book standard sedan car rental at SFO airport on Hertz", "https://hertz.com/rentacar/reservation/review", "Reservation Confirmed - Hertz",
         "<div class='rental-summary'><h2>Reservation #H89234 Confirmed</h2><span>Vehicle: Toyota Camry or similar (Standard Sedan)</span><span class='pickup'>Pick-up: San Francisco International Airport (SFO)</span><span class='total'>Total: $184.50</span></div>",
         [{"step": 1, "action": "click", "target": "button#submit-rental"}],
         None),
        ("travel_005", "Check Amtrak train schedule from Boston South Station to NYC", "https://amtrak.com/train-schedules", "Train Schedules & Fares - Amtrak",
         "<main><div class='train-result-card'><span class='train-name'>Acela 2151</span><span class='departure'>Depart: 07:15 AM BOS</span><span class='arrival'>Arrive: 10:55 AM NYP</span><span class='fare'>$128.00 Coach</span></div></main>",
         [{"step": 1, "action": "fill", "target": "input#origin", "value": "Boston (BOS)"}, {"step": 2, "action": "click", "target": "button#find-trains"}],
         None),
        ("travel_006", "Find pet-friendly cabin rental in Lake Tahoe on Airbnb", "https://airbnb.com/s/Lake-Tahoe/homes", "Lake Tahoe Cabins - Airbnb",
         "<div class='search-results-grid'><h1>Places to stay in Lake Tahoe (Pet-friendly)</h1><div class='listing-card'><h3>Cozy Tahoe Pine Chalet</h3><span class='rating'>4.96 (124 reviews)</span><span class='price'>$215 / night</span></div></div>",
         [{"step": 1, "action": "click", "target": "button#filter-pets"}, {"step": 2, "action": "click", "target": "button#apply-filters"}],
         None),
        ("travel_007", "Search Google Flights for roundtrip weekend getaway to Miami", "https://google.com/travel/flights/search", "Flights to Miami (MIA) - Google Flights",
         "<div class='flight-results-list'><h2>Best departing flights</h2><div class='itinerary-card'><span>American Airlines (Nonstop, 3h 10m)</span><span class='price'>$218</span><span class='emissions'>-12% emissions</span></div></div>",
         [{"step": 1, "action": "navigate", "target": "https://google.com/travel/flights"}, {"step": 2, "action": "click", "target": "button[aria-label='Search']"}],
         None),
    ]

    for tid, task, url, title, dom, trace, f_var in travel_success:
        tasks.append({
            "task_id": tid, "domain": "Travel & Search", "user_task": task, "ground_truth": "SUCCESS", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 4.2 PARTIAL (5)
    travel_partial = [
        ("travel_008", "Search flights from Chicago to Seattle on Skyscanner", "https://skyscanner.com", "Skyscanner | Compare Cheap Flights",
         "<div class='flight-search-form'><input id='origin-fld' value='Chicago O'Hare (ORD)'/><input id='dest-fld' value='Seattle-Tacoma (SEA)'/><input id='depart-date' value='2026-11-20'/><button id='search-flights-btn'>Search flights</button></div>",
         [{"step": 1, "action": "fill", "target": "input#origin-fld", "value": "Chicago O'Hare (ORD)"}, {"step": 2, "action": "fill", "target": "input#dest-fld", "value": "Seattle-Tacoma (SEA)"}],
         "unclicked_flight_search"),
        ("travel_009", "Select dates and guests for mountain lodge on VRBO", "https://vrbo.com/property/104928", "Serene Mountain Lodge - VRBO",
         "<div class='booking-sidebar'><div class='dates-box'><span>Nov 18 - Nov 23 (5 nights)</span></div><select id='guests'><option value='4' selected=''>4 Adults</option></select><button id='book-now-btn' class='btn'>Request to Book</button></div>",
         [{"step": 1, "action": "select", "target": "select#guests", "value": "4"}],
         "uncommenced_booking_request"),
        ("travel_010", "Fill passenger passport information for international flight on Delta", "https://delta.com/checkout/passengers", "Passenger Information - Delta",
         "<form class='passenger-form'><input name='first_name' value='David'/><input name='last_name' value='Miller'/><input name='passport_number' value='A98214029'/><button type='button' id='next-seats'>Select Seats & Review</button></form>",
         [{"step": 1, "action": "fill", "target": "input[name='passport_number']", "value": "A98214029"}],
         "unsubmitted_passenger_details"),
        ("travel_011", "Lookup subway transit directions from Times Square to Brooklyn Bridge", "https://maps.google.com", "Google Maps",
         "<div class='directions-card'><input id='start-point' value='Times Square, Manhattan, NY'/><input id='end-point' value='Brooklyn Bridge, New York, NY'/><button id='get-transit-directions'>Get Directions</button></div>",
         [{"step": 1, "action": "fill", "target": "input#start-point", "value": "Times Square, Manhattan, NY"}],
         "unsubmitted_navigation_query"),
        ("travel_012", "Select economy car class for airport car rental on Enterprise", "https://enterprise.com/en/reserve/vehicles", "Choose a Vehicle - Enterprise",
         "<div class='vehicle-carousel'><div class='car-card selected'><h4>Economy: Mitsubishi Mirage</h4><span class='rate'>$45/day</span><button class='btn-select-car'>Continue to Extras</button></div></div>",
         [{"step": 1, "action": "click", "target": "div.car-card"}],
         "unprogressed_rental_selection"),
    ]

    for tid, task, url, title, dom, trace, f_var in travel_partial:
        tasks.append({
            "task_id": tid, "domain": "Travel & Search", "user_task": task, "ground_truth": "PARTIAL", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 4.3 FAILED (6)
    travel_failed = [
        ("travel_013", "Book one-way flight from New York to Tokyo on United Airlines", "https://amazon.com", "Amazon.com: Online Shopping",
         "<main><div class='s-result-list'><h1>Results for 'Tokyo travel guide books'</h1></div></main>",
         [{"step": 1, "action": "navigate", "target": "https://amazon.com"}],
         "agent_drift_domain_mismatch"),
        ("travel_014", "Search flights from Boston to Miami on Spirit Airlines", "https://spirit.com/flights/search/error", "Service Unavailable - Spirit Airlines",
         "<main class='error-box'><h1>503 Service Unavailable</h1><p>Our flight booking servers are undergoing scheduled maintenance. Please try again later.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://spirit.com"}],
         "http_503_service_unavailable"),
        ("travel_015", "Search non-stop flights from London to Honolulu on Kayak", "https://kayak.com/flights/LON-HNL", "Search Flights - KAYAK",
         "<main class='results-empty'><h2>No non-stop flights found for this route</h2><p>Try enabling connecting flights or searching nearby departure airports.</p></main>",
         [{"step": 1, "action": "click", "target": "button[aria-label='Search flights']"}],
         "impossible_route_zero_results"),
        ("travel_016", "Check in online for flight AA-104 on American Airlines", "https://aa.com/checkin/denied", "Check-in Closed - American Airlines",
         "<div class='error-alert'><h3>Check-in Not Available</h3><p>Online check-in closes 45 minutes prior to domestic departures. Please proceed to airport ticket counter.</p></div>",
         [{"step": 1, "action": "click", "target": "button#submit-checkin"}],
         "checkin_deadline_expired"),
        ("travel_017", "Lookup weather history for year 1820 on AccuWeather", "https://accuweather.com/error", "Historical Data Error",
         "<div class='error-view'><h2>Unsupported Date Range</h2><p>Digital meteorological observation records are only available from 1950 onwards.</p></div>",
         [{"step": 1, "action": "fill", "target": "input#year", "value": "1820"}],
         "out_of_range_query_error"),
        ("travel_018", "Book luxury private yacht charter on Boatsetter", "https://wikipedia.org", "Yacht charter - Wikipedia",
         "<main><h1>Yacht charter</h1><p>A yacht charter is the practice of renting a sailboat or motor yacht and travelling to various coastal or island destinations.</p></main>",
         [{"step": 1, "action": "navigate", "target": "https://wikipedia.org/wiki/Yacht_charter"}],
         "hallucination_informational_drift"),
    ]

    for tid, task, url, title, dom, trace, f_var in travel_failed:
        tasks.append({
            "task_id": tid, "domain": "Travel & Search", "user_task": task, "ground_truth": "FAILED", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": ["Task terminated with error"], "network_logs": [{"status": 503, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    # 4.4 UNCERTAIN (2)
    travel_uncertain = [
        ("travel_019", "Solve Cloudflare Turnstile human verification challenge on Tripadvisor", "https://tripadvisor.com/challenge", "Just a moment...",
         "<div id='challenge-stage'><div class='cf-turnstile-wrapper'><iframe src='https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/b/turnstile/if/ov2' title='Widget containing a Cloudflare security challenge'></iframe></div><p>Verifying you are human. This may take a few seconds.</p></div>",
         [{"step": 1, "action": "navigate", "target": "https://tripadvisor.com"}],
         "cloudflare_turnstile_captcha_block"),
        ("travel_020", "Track live transatlantic flight radar location on FlightAware", "https://flightaware.com/live/flight/BAW178", "Live Flight Tracking - BAW178",
         "<div class='radar-view'><canvas id='map-gl-canvas' width='1400' height='700'></canvas><div class='satellite-status'>Connecting to ADS-B Satellite feed...</div></div>",
         [{"step": 1, "action": "navigate", "target": "https://flightaware.com/live/flight/BAW178"}],
         "webgl_radar_feed_unparsed"),
    ]

    for tid, task, url, title, dom, trace, f_var in travel_uncertain:
        tasks.append({
            "task_id": tid, "domain": "Travel & Search", "user_task": task, "ground_truth": "UNCERTAIN", "failure_variant": f_var,
            "outcome_spec": {"expected_url": url, "page_title": title, "intent_type": "respondent"},
            "evidence_package": {"audited_url": url, "page_title": title, "dom_summary": dom, "console_logs": [], "network_logs": [{"status": 200, "url": url}], "accessibility_tree": {"role": "WebArea", "name": title}},
            "action_trace": trace
        })

    return tasks

if __name__ == "__main__":
    dataset = generate_dataset()
    out_path = Path(__file__).resolve().parent / "curated_test_set.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    # Verification checks
    print(f"Total tasks generated: {len(dataset)}")
    gt_counts = {}
    domain_counts = {}
    for t in dataset:
        gt_counts[t["ground_truth"]] = gt_counts.get(t["ground_truth"], 0) + 1
        domain_counts[t["domain"]] = domain_counts.get(t["domain"], 0) + 1

    print("\nGround Truth Distribution:")
    for k, v in sorted(gt_counts.items()):
        print(f"  {k:10}: {v} ({v/len(dataset)*100:.1f}%)")

    print("\nDomain Distribution:")
    for k, v in sorted(domain_counts.items()):
        print(f"  {k:20}: {v} ({v/len(dataset)*100:.1f}%)")

    assert len(dataset) == 100, f"Expected 100 tasks, got {len(dataset)}"
    assert gt_counts == {"SUCCESS": 35, "PARTIAL": 25, "FAILED": 30, "UNCERTAIN": 10}, "Ground truth mismatch!"
    print(f"\n[OK] Benchmark dataset successfully written to {out_path}")
