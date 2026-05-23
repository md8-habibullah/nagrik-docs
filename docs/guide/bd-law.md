# Bangladesh Law AI Assistant

## BD Law Knowledge Base Strategy

Since we cannot train a custom model, we use **RAG (Retrieval-Augmented Generation)**:

```
User question (Bangla)
      │
      ▼
[Embed question] → find relevant law sections
      │
      ▼
[Retrieve top 3-5 relevant sections from BD law corpus]
      │
      ▼
[Claude 3.5 Sonnet] + retrieved context
      │
      ▼
[Answer in Bangla with citations]
```

---

## Key Laws to Include (Phase 1)

| Law                                          | Why Important              |
| -------------------------------------------- | -------------------------- |
| The Code of Criminal Procedure (CrPC)        | FIR filing, arrest rights  |
| Penal Code 1860                              | Common crimes, penalties   |
| Information & Communication Technology Act   | Digital crimes             |
| Women and Children Repression Prevention Act | Harassment, assault        |
| Consumer Rights Protection Act               | Product/service complaints |
| Road Transport Act 2018                      | Traffic laws, accidents    |
| Environmental Conservation Act               | Pollution complaints       |
| Tenant/Landlord Laws                         | Housing disputes           |
| Labor Act 2006                               | Worker rights              |
| RTI Act (Right to Information)               | Information requests       |

---

## BD Law System Prompt

```typescript
export const BD_LAW_SYSTEM_PROMPT = \`
You are "আইন সহায়ক" (Law Helper), an AI legal assistant
specialized in Bangladesh law.

## Your role
- Answer questions about Bangladesh laws in simple Bangla
- Cite specific sections when relevant
- Explain rights and procedures clearly
- Recommend when to consult a real lawyer

## Critical rules
1. ALWAYS clarify: you are an AI, not a licensed lawyer
2. For serious criminal matters → recommend police + lawyer
3. Never give advice that could endanger safety
4. Use plain Bangla, avoid legal jargon
5. Cite specific acts: "ফৌজদারি কার্যবিধি ধারা ১৫৪" etc.

## Response format
1. Direct answer to question
2. Relevant law section (if applicable)
3. Practical next step
4. "একজন আইনজীবীর সাথে কথা বলুন" reminder if complex

## Laws you know
[Insert full law corpus text here as context]
\`;
```

---

## Law Q&A Endpoint

```typescript
// src/routes/law.ts

router.post('/ask', async (req, res) => {
  const { question, history = [] } = req.body;

  // Set up streaming response
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const stream = await openRouterService.streamLawAnswer(
    question,
    history
  );

  for await (const chunk of stream) {
    const content = chunk.choices[0]?.delta?.content ?? '';
    if (content) {
      res.write(\`data: \${JSON.stringify({ content })}\\n\\n\`);
    }
  }

  res.write('data: [DONE]\\n\\n');
  res.end();
});
```

---

## Flutter - Streaming Law Response

````dart
// Receive server-sent events for streaming response

Stream<String> streamLawAnswer(String question, List history) async* {
  final request = http.Request(
    'POST',
    Uri.parse('\${Env.apiUrl}/api/law/ask'),
  );

  request.headers['Authorization'] = 'Bearer \$token';
  request.headers['Content-Type'] = 'application/json';
  request.body = jsonEncode({ 'question': question, 'history': history });

  final response = await client.send(request);

  await for (final chunk in response.stream
      .transform(utf8.decoder)
      .transform(const LineSplitter())) {

    if (chunk.startsWith('data: ')) {
      final data = chunk.substring(6);
      if (data == '[DONE]') break;
      final json = jsonDecode(data);
      yield json['content'] as String;
    }
  }
}
```\n\n
````
