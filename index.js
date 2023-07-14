require('dotenv').config();
const cors=require('cors')
const express=require('express')
const Stripe=require("stripe");

const app=express();
app.use(cors())
app.use(express.json());

console.log("key",process.env.PRIVATE_KEY)
const stripe=Stripe(process.env.PRIVATE_KEY);


const mongoose=require('mongoose');
const UserSchema = require('./schemas/user');
mongoose.connect(process.env.MONGO_DB).then(
    console.log('connected')
)



app.get('/',async (req,res)=>{
    
    res.json({"message":"hello revcieved"})
   
})


app.get('/getUser/:username',async (req,res)=>{
    try {
        
    const user=await UserSchema.findOne({user_name:req.params.username})
    if(user){
        return res.json({user,code:201})
    }
    res.json({message:"no user found"})
    } catch (error) {
        res.json({error})
    }
    
    
   
})

// a caller needs to encodeURIComponent in front end
app.post('/payment',async (req,res)=>{
    const decodedId = decodeURIComponent(req.body.username);
    const username=decodedId;

    const orderDetails = {
        productID: 1,
        productName: "Text",
        productPrice: 2,
        buyerID: 1,
        buyerEmail: "mujee@gmail.com",
      };

      let paymentMethod = await stripe.paymentMethods.create({
        type: "card",
        card: {
          number: "4242424242424242",
          exp_month: 9,
          exp_year: 2023,
          cvc: "314",
        },
      });

      let paymentIntent = await stripe.paymentIntents.create({
        amount: 1 * 100,
        currency: "usd",
        payment_method_types: ["card"],
        payment_method: paymentMethod.id,
        confirm: true,
      });
      if (paymentIntent) {
        const user=await UserSchema.findOne({user_name:req.params.user_name})
        if(user){
            console.log(user)
            const data =await UserSchema.findByIdAndUpdate(user._id,req.body,{
                new:true
               })
        }else{
            const data=await UserSchema.create(req.body)

        }
        
        return res.status(201).json({ message: "Order created" });
      } else {
        return res.status(400).json({ err: "Something went wrong" });
      }
  

    
   
})

app.listen(5000)